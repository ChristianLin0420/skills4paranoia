#!/usr/bin/env python3
"""Probes for lucidrains/robo_ttt @ df865de, against arXiv:2607.15275.

Each probe states a hypothesis, prints a measurement, and names both outcomes, so
the verdict does not depend on the reader trusting the person who ran it.

    python probes.py /path/to/robo_ttt        # needs torch >= 2.5
"""
import sys
CODE = sys.argv[1] if len(sys.argv) > 1 else "."

import torch
import torch.nn.functional as F
from torch import nn
from torch.func import functional_call
sys.path.insert(0, CODE)
from robo_ttt import MemoryKeyValueBind, TTTWrapper, RoboTTT

torch.manual_seed(0)
D, N, T, B = 16, 4, 5, 2

def mk():
    net = nn.Sequential(nn.Linear(D, 2*D), nn.GELU(), nn.Linear(2*D, D))
    return TTTWrapper(D, memory = MemoryKeyValueBind(D, net))

# ---------- 1. README basic usage ----------
w = mk()
x = torch.randn(B, T, N, D)
out, nfw, inter = w(x)
print("1 shapes  in", tuple(x.shape), "-> out", tuple(out.shape))
print("1 fast weight keys:", sorted(nfw.fast_weights.keys()), "step:", nfw.step)

# ---------- 2. gate at init ----------
w2 = mk()
g = w2.memory_out_layerscale
print(f"2 gate init: mean={g.mean().item():+.3e} std={g.std().item():.3e} max|.|={g.abs().max().item():.3e}")

# ---------- 3. does TTTWrapper already add the residual? ----------
w3 = mk()
with torch.no_grad(): w3.memory_out_layerscale.zero_()
o3, _, _ = w3(x)
print(f"3 gate=0 -> ||out - in|| = {(o3 - x).abs().max().item():.3e}   (0 means the wrapper returns input + gated)")

# ---------- 4. RoboTTT hook: is the residual applied twice? ----------
class Tiny(nn.Module):
    def __init__(self):
        super().__init__()
        self.to_action_tokens = nn.Identity()
    def forward(self, video_hiddens, time = None, return_unreduced_loss = False):
        h = self.to_action_tokens(video_hiddens)          # (b*t, n, d)
        return h.mean(dim = (-1, -2))                     # per-sample scalar

policy = Tiny()
model = RoboTTT(policy, ttt_wrapper = mk(), ttt_module_paths = ('to_action_tokens',),
                batch_time_arg = 'video_hiddens', times_arg = None, unreduced_loss_arg = None)
with torch.no_grad():
    for ws in model.ttt_wrappers: ws.memory_out_layerscale.zero_()

vh = torch.randn(B, T, N, D)
hooked = model(video_hiddens = vh)                        # (b, t)
plain  = policy(vh.reshape(B*T, N, D)).reshape(B, T)      # no hook at all
ratio  = (hooked / plain)
print(f"4 hooked/unhooked ratio: min={ratio.min().item():.6f} max={ratio.max().item():.6f}")
print(f"4 expected 1.0 if Eq.3 is O = attn + tanh(a)*TTT ; 2.0 if the residual is added twice")

print()
from torch import nn
from robo_ttt import MemoryKeyValueBind, TTTWrapper, RoboTTT
from robo_ttt.robo_ttt import sample_action_times, newtonschulz5
D, N, T, B = 16, 4, 6, 2
net = lambda: nn.Sequential(nn.Linear(D, 2*D), nn.GELU(), nn.Linear(2*D, D))

# --- A. inner learning rate actually used ---
m = MemoryKeyValueBind(D, net())
print(f"A raw lr param = {m.learnable_lr.item():.4f} -> softplus = {F.softplus(m.learnable_lr).item():.4f}  (paper: base 0.1)")
print(f"A learned_forget default = {m.learned_forget} ; muon default = {m.muon_update} ; rope theta = {m.rotary_emb.freqs.shape}")

# --- B. does one update reduce the fast-weight loss? (Eq.1 sign) ---
m2 = MemoryKeyValueBind(D, net(), learned_forget = False, rotary_embed_qk = False)
tok = torch.randn(1, N, D)
qkv = m2.to_qkv(tok); q,k,v = m2.split_qkv(qkv)
base = {n: p.unsqueeze(0) for n,p in m2.base_memory_params.items()}
from torch.func import functional_call
before = F.mse_loss(m2.retrieve(base, k), v).item()
_, delta = m2(tok)
after  = F.mse_loss(m2.retrieve({n: base[n] + delta[n] for n in base}, k), v).item()
print(f"B fast-weight MSE on its own keys: before={before:.6f} after={after:.6f}  -> {'DESCENDS (Eq.1 sign correct)' if after < before else 'ASCENDS (sign wrong)'}")

# --- C. TBPTT: does the gradient actually stop at a segment boundary? ---
def grad_reach(seg):
    w = TTTWrapper(D, memory = MemoryKeyValueBind(D, net()), tbptt_step_size = seg)
    xs = [torch.randn(B, 1, N, D, requires_grad = True) for _ in range(T)]
    out, _, _ = w(torch.cat(xs, dim = 1))
    out[:, -1].sum().backward()
    return [0 if x.grad is None else float(x.grad.abs().sum()) for x in xs]
for seg in (None, 2, 3):
    g = grad_reach(seg)
    reach = sum(1 for v in g if v > 0)
    print(f"C tbptt_step_size={str(seg):4s} -> timesteps with nonzero grad from the last output: {reach}/{T}  {['%.2e'%v for v in g]}")

# --- D. sequence action forcing: one noise level per (batch,time)? ---
tau = sample_action_times(B*T)
print(f"D sample_action_times({B*T}) -> shape {tuple(tau.shape)} range [{tau.min():.4f},{tau.max():.4f}]  (paper: tau = 0.999*(1-u), u~Beta(1.5,1))")
big = sample_action_times(200000); print(f"D empirical mean={big.mean():.4f}  closed form 0.999*(1-1.5/2.5)={0.999*(1-1.5/2.5):.4f}")

# --- E. what does finetune_parameters actually expose? ---
class Tiny(nn.Module):
    def __init__(s):
        super().__init__(); s.backbone = nn.Linear(D, D); s.to_action_tokens = nn.Identity()
    def forward(s, video_hiddens, **kw):
        return s.to_action_tokens(s.backbone(video_hiddens)).mean(dim=(-1,-2))
p = Tiny()
mod = RoboTTT(p, ttt_wrapper = TTTWrapper(D, memory = MemoryKeyValueBind(D, net())),
              ttt_module_paths = ('to_action_tokens',), batch_time_arg = 'video_hiddens',
              times_arg = None, unreduced_loss_arg = None)
tot = sum(q.numel() for q in mod.parameters()); ft = sum(q.numel() for q in mod.finetune_parameters())
print(f"E params total={tot} finetune_parameters()={ft} ({100*ft/tot:.1f}%)  policy params excluded = {ft < tot}")

# --- F. loss masking: do masked timesteps still update the fast weights? ---
mask = torch.tensor([[True, False, False, False, False, True]]*B)
vh = torch.randn(B, T, N, D)
l_masked = mod(video_hiddens = vh, loss_mask = mask)
_, fw = mod(video_hiddens = vh, prev_fast_weights = None, return_fast_weights = True)
print(f"F masked loss = {float(l_masked):.6f} ; fast-weight step advanced to {fw[0].step} of T={T} (paper: all steps update W, loss only on unmasked)")
