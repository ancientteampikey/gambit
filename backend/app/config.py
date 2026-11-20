from pathlib import Path
import os

ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = ROOT / "data"
DATA_DIR.mkdir(exist_ok=True)
DATABASE_URL = os.getenv("GAMBIT_DATABASE_URL", f"sqlite:///{DATA_DIR / 'gambit.db'}")
def _stockfish_path() -> str:
    configured = os.getenv("GAMBIT_STOCKFISH_PATH", "")
    if configured:
        return configured
    candidates = (ROOT / "stockfish" / "stockfish.exe", ROOT / "stockfish" / "Stockfish-master" / "src" / "stockfish.exe")
    return next((str(path) for path in candidates if path.is_file()), "")

STOCKFISH_PATH = _stockfish_path()
ENGINE_THREADS = int(os.getenv("GAMBIT_ENGINE_THREADS", "2"))
ENGINE_HASH_MB = int(os.getenv("GAMBIT_ENGINE_HASH_MB", "128"))
