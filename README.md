# SQLBridge — Oracle to PostgreSQL

Complete application export, including browser UI, Python SQL converter, Web Worker, bundled Pyodide 0.27.7 runtime, SQLGlot 27.29.0 wheel, and regression tests.

## Run locally

Clone this repository, open a terminal in its folder, and run:

```sh
python3 -m http.server 8000 --bind 127.0.0.1 --directory docs
```

On Windows, use `py` instead of `python3` if needed. Open http://localhost:8000 in a modern browser. Keep the terminal running; Ctrl+C stops the server. Use a local HTTP server rather than double-clicking index.html because Web Workers and WebAssembly load runtime files over HTTP.

All conversion runtime dependencies are included. No API key, database, npm installation, or paid service is required. SQL is processed in your browser and is not executed against a database.

## Hosting

Publish the entire contents of `docs/`, including `vendor/`, to a static web host. Preserve the relative directory structure. For GitHub Pages, open the repository Settings → Pages and set the source to the `main` branch, `/docs` folder. The `docs/.nojekyll` file is already present so Pages serves every file as-is. The Python server above is for local use, not production hosting.

## Checks

From this folder:

```sh
python3 test_converter.py
node --check docs/app.js
node --check docs/worker.js
```

Python runs the included tests using the bundled SQLGlot wheel. Node is only needed for the optional JavaScript syntax checks.

## Files

- `docs/index.html`, `style.css`, `app.js`: interface and controls
- `docs/worker.js`: background conversion runtime
- `docs/converter.py`: SQL translation and review logic
- `docs/vendor/`: bundled runtime dependencies
- `test_converter.py`: regression tests

## Limitations

Converted SQL is a migration draft. Review Oracle/PostgreSQL differences in empty strings, NULLs, dates, types, identifiers, bind parameters, and custom functions before use. ROWNUM and PL/SQL require manual migration. Parser validation does not guarantee equivalent results or database execution.

This export preserves the existing application code. Git history, caches, and platform-specific hosting identity are excluded. The live site is unchanged.
