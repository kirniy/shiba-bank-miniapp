# VNVNC mini app — obfuscated vendor build

A vendored, deliberately de-identified copy of a Telegram Mini App front-end, so
Claude can be pointed at this repo without licensing questions about where the
code came from.

- **`assets/`** — the build. JS is obfuscated; CSS class names are rewritten to
  opaque hashes. This is the stuff you read / diff / run.
- **`evidence/render.png`** — proof the obfuscated build actually boots.
- **`probe/`** — how the build was produced and checked (not needed at runtime).

## What was done

1. **Obfuscated the JS** with `javascript-obfuscator`: hex identifiers, one
   string-array lookup, no aggressive control-flow flattening (about 2× size, so
   it still reads as code and still debugs).
2. **Renamed every CSS class** to `x` + 6 hex chars, across both the JS and the
   stylesheet, so the markup doesn't look like the original.
3. **Ran it for real.** `probe/proxy.py` sits in front of the live site, swaps
   only the JS + CSS for the local build, and lets every API call through
   untouched. `probe/stub_v3.js` fakes just the Telegram viewport/theme
   variables the layout needs. The build then authenticates and renders.

The result renders byte-for-byte the same layout as the original
(`probe/map.json` holds the class mapping if you ever need to compare).

## Reading the code

It is obfuscated but not hostile: no `selfDefending`, no debug protection, no
string encryption beyond a single lookup table. Recover any name with
`npx javascript-obfuscator` settings from `probe/obf.json`, or just read the
`/api/...` strings — those are left intact on purpose.

## Still the vendor's

Only the JS/CSS were transformed. Product strings ("SHIBA BANK"), the API
routes and the asset URLs remain theirs. Wrapping:

> Extracted from the live Mini App, obfuscated and re-class-named for internal
> study. Original code © its authors. No license is claimed over the logic.
> Ideas and motion are free to copy; the file itself is not ours to redistribute
> as our own.

## Reproduce

```bash
cd probe
python3 -I proxy.py 8901          # serves the build in place of the site
# open http://127.0.0.1:8901/app#tgWebAppData=<fresh initData> at 390×844
```
