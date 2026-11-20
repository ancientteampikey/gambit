import asyncio
from pathlib import Path
import chess
import chess.engine
from ..config import ENGINE_HASH_MB, ENGINE_THREADS, STOCKFISH_PATH
from .openings import repertoire_move

class EngineUnavailable(RuntimeError): pass

class ChessEngine:
    def __init__(self):
        self._engine: chess.engine.SimpleEngine | None = None
        self._lock = asyncio.Lock()
        self._path = STOCKFISH_PATH

    def status(self):
        return {"available": self._engine is not None, "path": self._path or None,
                "message": "Ready" if self._engine else "Stockfish is not configured. Set GAMBIT_STOCKFISH_PATH in .env or Settings."}

    async def start(self, path: str | None = None):
        candidate = path or self._path
        if not candidate or not Path(candidate).is_file():
            return self.status()
        async with self._lock:
            await asyncio.to_thread(self._close_sync)
            try:
                self._engine = await asyncio.to_thread(chess.engine.SimpleEngine.popen_uci, candidate)
                await asyncio.to_thread(self._engine.configure, {"Threads": ENGINE_THREADS, "Hash": ENGINE_HASH_MB})
                self._path = candidate
            except Exception as exc:
                self._engine = None
                raise EngineUnavailable(f"Could not start Stockfish: {exc}") from exc
        return self.status()

    def _close_sync(self):
        if self._engine:
            try: self._engine.quit()
            finally: self._engine = None

    async def close(self):
        async with self._lock:
            await asyncio.to_thread(self._close_sync)

    async def candidates(self, board: chess.Board, time_ms: int, multipv: int = 5):
        if not self._engine: raise EngineUnavailable(self.status()["message"])
        limit = chess.engine.Limit(time=max(time_ms / 1000, 0.05))
        async with self._lock:
            return await asyncio.to_thread(self._engine.analyse, board, limit, multipv=multipv)

    async def choose_move(self, board: chess.Board, profile, time_ms: int):
        book_move = repertoire_move(board, profile.opening, board.turn)
        if book_move: return book_move, {"source": "repertoire", "score": None, "pv": [book_move.uci()]}
        lines = await self.candidates(board, time_ms, 5)
        if not isinstance(lines, list): lines = [lines]
        ranked = sorted(lines, key=lambda line: self._style_score(board, line, profile), reverse=True)
        best = ranked[0]
        move = best["pv"][0]
        score = best["score"].pov(board.turn).score(mate_score=100000)
        return move, {"source": "engine", "score": score, "pv": [m.uci() for m in best.get("pv", [])]}

    def _style_score(self, board, line, profile):
        pov = line["score"].pov(board.turn).score(mate_score=100000) or 0
        move = line["pv"][0]
        is_capture = board.is_capture(move)
        gives_check = board.gives_check(move)
        style = profile.style.lower()
        bonus = 0
        if style == "aggressive": bonus += 18 * gives_check + 8 * is_capture
        elif style == "chaos": bonus += 25 * gives_check + 14 * is_capture + (profile.risk // 7)
        elif style == "defensive": bonus += 10 if not is_capture else 0
        # Never allow the personality layer to choose a clearly inferior line.
        return pov + bonus

engine_service = ChessEngine()
