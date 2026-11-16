# Shiba Bank — Mini App

Front-end bundle for the Shiba Bank Telegram Mini App: buy and sell Telegram
Stars, Telegram Premium, and wallet top-ups.

```bash
npm i -g javascript-obfuscator   # only needed to rebuild
```

- **`assets/`** — production build (`app.<hash>.js`, `app.<hash>.css`).
- **`evidence/render.png`** — the build running against the API.
- **`probe/`** — local harness for running the bundle outside Telegram.

## Build

The bundle ships obfuscated. A Mini App is served to every client that opens
it, so the source is always one devtools panel away; hex identifiers and a
shuffled string table keep the structure from being read at a glance while
staying debuggable (no self-defending code, no debug protection, ~2× size).
CSS class names are generated hashes so internal selector names never leak into
the pages that embed the app.

Obfuscator settings: `probe/obf.json`.

## Running locally

The bundle expects the Telegram WebView globals. `probe/proxy.py` serves the
local build and proxies API traffic to the backend; `probe/stub_v3.js`
provides the viewport and theme variables the layout needs.

```bash
cd probe
python3 -I proxy.py 8901
# open http://127.0.0.1:8901/app#tgWebAppData=<initData> at 390×844
```

`probe/map.json` maps hashed class names back to readable selectors — keep it
alongside any rebuild.

## Layout

`html` gets `.gate` until the app boots, then the class is removed and the
loader swaps the gate box out. Skins and themes are driven by CSS custom
properties (`--tg-theme-*` reflect Telegram's own theme params).

## License

MIT — see [LICENSE](LICENSE).
