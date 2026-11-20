# Development log

## 2026-11-20 — Initial working foundation

- Created separated FastAPI/SQLite and React/Vite application structure.
- Implemented legal-move backend API, bot profile CRUD, opening repertoire rules, UCI Stockfish lifecycle, personality-aware MultiPV selection, and PGN analysis endpoint.
- Added responsive dark UI for dashboard, play, bot editor, analysis, and Stockfish settings.
- Added Windows launcher, setup documentation, and core chess/opening tests.
- Stockfish is intentionally not bundled or downloaded; configure its verified local executable in Settings.
- Verification: frontend production build succeeds; backend core/API suite passes (5 tests). Stockfish smoke testing remains pending because no local executable was present.
- Imported the user-provided Stockfish source into `stockfish/Stockfish-master`; added a Windows build helper and automatic executable discovery. Compilation remains blocked until a C++ build toolchain is installed.
- Added production Docker deployment: React is served from FastAPI and Stockfish is built from source in the image; included a Render Blueprint with persistent SQLite storage.
