#!/usr/bin/env bash
# Install the typeset fonts into ~/Library/Fonts so Keynote resolves them.
#
# The SVG preview pulls these from Google Fonts and needs nothing installed.
# The .pptx only stores font *names*, so whichever machine opens the deck must
# have them locally or Keynote silently substitutes and the layout shifts.
#
#   ./scripts/install-fonts.sh            # plex  (IBM Plex Sans/Mono + Noto Sans TC)
#   ./scripts/install-fonts.sh plex-full  # adds IBM Plex Sans TC from IBM's release
#   ./scripts/install-fonts.sh inter      # Inter + Noto Sans TC + JetBrains Mono
set -euo pipefail

SET="${1:-plex}"
DEST="$HOME/Library/Fonts"
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT

case "$SET" in
  plex)      GF=("IBM Plex Sans" "IBM Plex Mono" "Noto Sans TC"); PLEX_TC=0 ;;
  plex-full) GF=("IBM Plex Sans" "IBM Plex Mono"); PLEX_TC=1 ;;
  inter)     GF=("Inter" "JetBrains Mono" "Noto Sans TC"); PLEX_TC=0 ;;
  system)    echo "typeset 'system' uses macOS built-ins — nothing to install."; exit 0 ;;
  *)         echo "unknown typeset: $SET (plex | plex-full | inter | system)" >&2; exit 2 ;;
esac

echo "Installing typeset '$SET' into $DEST"
printf '  from Google Fonts: %s\n' "${GF[*]}"
[ "$PLEX_TC" = 1 ] && echo "  from github.com/IBM/plex: IBM Plex Sans TC"
read -r -p "Continue? [y/N] " ok
[ "$ok" = "y" ] || [ "$ok" = "Y" ] || { echo "aborted"; exit 1; }

mkdir -p "$DEST"

for fam in "${GF[@]}"; do
  slug="${fam// /%20}"
  echo "-- $fam"
  curl -fsSL -o "$TMP/f.zip" "https://fonts.google.com/download?family=$slug"
  unzip -qo "$TMP/f.zip" -d "$TMP/f"
  find "$TMP/f" \( -name '*.ttf' -o -name '*.otf' \) -exec cp {} "$DEST/" \;
  rm -rf "$TMP/f" "$TMP/f.zip"
done

if [ "$PLEX_TC" = 1 ]; then
  echo "-- IBM Plex Sans TC"
  url=$(curl -fsSL https://api.github.com/repos/IBM/plex/releases/latest \
        | grep -o 'https://[^"]*[Ss]ans[-_]*TC[^"]*\.zip' | head -1)
  if [ -z "$url" ]; then
    echo "   could not find a Plex Sans TC asset in the latest release." >&2
    echo "   download it manually from https://github.com/IBM/plex/releases" >&2
  else
    curl -fsSL -o "$TMP/tc.zip" "$url"
    unzip -qo "$TMP/tc.zip" -d "$TMP/tc"
    find "$TMP/tc" \( -name '*.ttf' -o -name '*.otf' \) -exec cp {} "$DEST/" \;
  fi
fi

echo "Done. Restart Keynote so it picks up the new families."
