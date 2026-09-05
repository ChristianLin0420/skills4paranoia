# 產出

這個 skill 不附任何腳本。產檔的程式碼由 agent 當場寫，寫完就丟。下面是規格與踩過的坑。

## 選哪個格式

| 需求 | 產出 | 作法 |
|---|---|---|
| 給人看、投影、印 PDF | 單檔 HTML | 直接寫 HTML，零相依 |
| 要在 Keynote / PowerPoint 裡編輯 | `.pptx` | 當場寫 python-pptx 程式碼 |
| 兩者都要 | 先 HTML 確認排版，再產 pptx | 同一份 deck.md 產兩次 |

先產 HTML 看一眼，排版對了再產 pptx —— pptx 每次都要開 Keynote 才看得到，迭代很慢。

## HTML

一個檔案，內嵌每一頁的 SVG（`viewBox="0 0 960 540"`），字型用 `<link>` 從 Google Fonts 取。這樣不需安裝任何東西就能看到真正的字。

```html
<!doctype html>
<meta charset="utf-8">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:wght@400;500&family=IBM+Plex+Mono:wght@400;500&family=Noto+Sans+TC:wght@400;500&display=swap">
<style>
body{margin:0;padding:28px;background:#E7E8EA;font:13px/1.5 -apple-system,sans-serif}
.s{margin:0 0 22px;border-radius:3px;overflow:hidden;box-shadow:0 1px 3px rgba(0,0,0,.14)}
svg{display:block;width:100%;height:auto}
</style>
<div class="s"><svg viewBox="0 0 960 540">…</svg></div>
```

SVG 的注意事項：

- 每個 `<text>` 都要自己算換行，拆成多個 `<tspan x= y=>`。中日韓字寬約等於字級，拉丁小寫約 0.50、大寫與數字約 0.58。
- 基線位置：`top + size × (leading − 0.30)`，之後每行加 `size × leading`。這樣才對得上 PowerPoint 的行框行為。
- 字距用 `letter-spacing`（單位同 viewBox，即 pt）。
- 對齊用 `text-anchor` 搭配 x：靠左用 `start` 且 x = 左緣；置中用 `middle` 且 x = 中心；靠右用 `end` 且 x = 右緣。
- 折線用 `<polyline fill="none">`，誤差帶用 `<polygon>` 無 stroke。
- 列印成 PDF 時每頁一張，加 `@page{size:960pt 540pt;margin:0}` 與 `.s{page-break-after:always}`。

## .pptx

用 python-pptx。畫布設成 960 × 540 pt，用空白版面，所有東西都是自己畫的形狀，不用內建佔位框。

```python
from pptx import Presentation
from pptx.util import Emu, Pt
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import MSO_ANCHOR, PP_ALIGN
from pptx.oxml.ns import qn

prs = Presentation()
prs.slide_width = Emu(int(Pt(960)))
prs.slide_height = Emu(int(Pt(540)))
blank = prs.slide_layouts[6]

slide = prs.slides.add_slide(blank)
slide.background.fill.solid()
slide.background.fill.fore_color.rgb = RGBColor.from_string("F1F2F3")
```

### 踩過的坑

**中日韓字型要另外設。** `run.font.name` 只設拉丁字型，中文會掉回預設字。必須直接寫 XML，`latin`、`ea`、`cs` 三個都設：

```python
rPr = run._r.get_or_add_rPr()
for tag, face in (("a:latin", "IBM Plex Sans"), ("a:ea", "Noto Sans TC"), ("a:cs", "IBM Plex Sans")):
    el = rPr.find(qn(tag))
    if el is None:
        el = rPr.makeelement(qn(tag), {}); rPr.append(el)
    el.set("typeface", face)
```

**字距沒有 API。** 設 `rPr` 的 `spc` 屬性，單位是百分之一 pt：`rPr.set("spc", str(int(tracking * 100)))`。

**文字框預設有內距。** 四邊 margin 都設 0，否則位置全部偏掉：

```python
tf = box.text_frame
tf.word_wrap = True
tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0
tf.vertical_anchor = MSO_ANCHOR.TOP        # 或 MIDDLE / BOTTOM
p.alignment = PP_ALIGN.LEFT                # 或 CENTER / RIGHT
p.line_spacing = 1.45                      # 浮點數是倍數
```

**形狀預設帶陰影。** 每個形狀都要 `shp.shadow.inherit = False`，否則 Keynote 會畫出預設投影。

**圓角矩形的圓角要自己算。** `shp.adjustments[0] = radius / min(w, h)`，且上限 0.5。寬或高小於 1.5pt 就改用直角矩形，否則圓角會吃掉整個形狀。

**折線不能用預設的 close。** `add_line_segments(pts, close=False)`，預設 `True` 會把終點連回起點畫出一條多餘的線：

```python
b = shapes.build_freeform(pts[0][0], pts[0][1], Pt(1))   # scale = EMU per unit
b.add_line_segments(pts[1:], close=False)
shp = b.convert_to_shape()
shp.fill.background()
shp.line.color.rgb = RGBColor.from_string("3A6183")
shp.line.width = Pt(1.8)
```

誤差帶則相反：把上界正走、下界反走串成一圈，`close=True`，填色、`shp.line.fill.background()` 不描邊。

**圖片會被拉變形。** 用 `pptx.parts.image.Image.from_file(path).size` 取像素尺寸，自己算等比縮放後置中，不要直接把 width 和 height 都塞進 `add_picture`。

**細線用矩形不要用 connector。** 高度 0.75pt 的矩形在 Keynote 裡比 connector 穩定。

**講者備忘**：`slide.notes_slide.notes_text_frame.text = "…"`。

### 產完檢查

不要只看有沒有跑完，打開檔案驗這幾件事：

```python
from pptx import Presentation
import re
p = Presentation(out)
xml = "".join(s.shapes._spTree.xml for s in p.slides)
assert round(p.slide_width / 12700) == 960
print(sorted(set(re.findall(r'typeface="([^"]+)"', xml))))   # 中英字型都要在
```

再確認沒有任何形狀跑出 0–960 / 0–540 的範圍。最常見的成因是座標軸刻度上限小於資料最大值，線就會畫到框外面 —— 見 `research-figures` 第 3 節。

## 字型安裝

`.pptx` 只記字型名稱，開檔的機器沒裝就會被 Keynote 靜默替換、版面位移。要把預設的 IBM Plex + 思源黑體裝起來：從 Google Fonts 下載 `IBM Plex Sans`、`IBM Plex Mono`、`Noto Sans TC`，解壓後把 ttf/otf 放進 `~/Library/Fonts`，重開 Keynote。

`IBM Plex Sans TC` 不在 Google Fonts 上，要從 github.com/IBM/plex 的 release 取。

要傳給沒裝字型的人（尤其 Windows），改用 `typeface: system`（Helvetica Neue + PingFang TC + Menlo），全 macOS 內建。
