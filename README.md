# GAMBIT Chess Engine

GAMBIT is a local Windows chess application with a FastAPI/SQLite backend, a React board, persistent bot profiles, and a real UCI Stockfish integration. Personality choices rank Stockfish MultiPV candidates; they never fabricate engine evaluation or use random legal moves.

## Start on Windows

1. Install Python 3.11+ and Node.js 20+.
2. Either download a Windows Stockfish build from [the official Stockfish site](https://stockfishchess.org/download/), or compile the bundled `stockfish/Stockfish-master` source with `build_stockfish.bat`. The latter requires Visual Studio 2022 Build Tools and its **Desktop development with C++** workload.
3. Double-click `start.bat`.
4. Open `http://localhost:5173`, then enter the executable path on **Settings** and choose **Start engine**.

`start.bat` creates `.venv`, installs backend/frontend dependencies, and opens separate backend and frontend consoles. It intentionally does not download an executable engine.

### Compile the provided Stockfish source

The supplied `Stockfish-master.zip` source has been unpacked into `stockfish/Stockfish-master`. Its license remains GPLv3. To create the executable, install Visual Studio Build Tools 2022 with **Desktop development with C++**, open **x64 Native Tools Command Prompt for VS 2022**, and run `build_stockfish.bat` from this project directory. The script writes `stockfish/stockfish.exe`; `start.bat` discovers it automatically.

## Manual start

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r backend\requirements.txt
npm.cmd --prefix frontend install
python -m uvicorn app.main:app --app-dir backend --reload
# Separate terminal:
npm.cmd --prefix frontend run dev
```

## Public web deployment

The project includes a production [Dockerfile](Dockerfile) and `render.yaml`. The Docker build compiles the included Stockfish source on Linux, builds the React frontend, and serves both UI and API from one FastAPI service. It needs no locally compiled `stockfish.exe`.

To publish it using Render: create a Git repository containing this project, push it to GitHub/GitLab, then choose **New + → Blueprint** in Render and select the repository. Render reads `render.yaml`; approve the persistent disk if you want bot profiles and games to survive deployments. When the build finishes, Render gives you the public HTTPS URL.

For another host, deploy the `Dockerfile` as a single container and attach persistent storage at `/app/data`. Do not use serverless-only hosting for this version: it needs a long-lived Stockfish process and SQLite storage.

## Functionality

- Create, edit, duplicate, and delete persistent SQLite bot profiles.
- Play legal moves via click/drag chessboard; backend validates every move.
- Ask a configured Stockfish process for bot replies, with opening repertoire and personality-aware MultiPV ranking.
- Import PGN in the analysis page and get real engine scores, best moves, and GAMBIT’s move labels.
- Validate FEN/PGN API input, detect game end state, identify included openings, and configure the engine at runtime.

## API

Swagger UI is available at `http://localhost:8000/docs`. Engine-dependent endpoints return HTTP 503 until Stockfish is configured; the UI presents that state explicitly.

## Tests

```powershell
.\.venv\Scripts\python.exe -m pytest backend/tests
```

Tests cover opening matching, colour-aware repertoire selection, checkmate, and stalemate. A Stockfish smoke test must be run locally once a trusted `stockfish.exe` is configured.
