import chess
import chess.pgn
from io import StringIO
from ..engine.service import engine_service
from ..engine.openings import identify

PIECE_VALUES = {chess.PAWN: 100, chess.KNIGHT: 320, chess.BISHOP: 330, chess.ROOK: 500, chess.QUEEN: 900}

def _label(loss: int, sacrificed: bool) -> tuple[str, str]:
    if sacrificed and loss < 40: return "Brilliant", "A sound material sacrifice preserves the engine evaluation."
    if loss <= 15: return "Best", "Matches the engine's preferred continuation."
    if loss <= 45: return "Excellent", "Keeps the position close to optimal."
    if loss <= 90: return "Good", "Playable, but the engine finds a more accurate move."
    if loss <= 180: return "Inaccuracy", "Gives up a noticeable amount of evaluation."
    if loss <= 350: return "Mistake", "Allows a substantially stronger reply."
    return "Blunder", "Loses significant evaluation according to the engine."

async def analyze_game(pgn_text: str, depth: int):
    game = chess.pgn.read_game(StringIO(pgn_text))
    if game is None: raise ValueError("Invalid PGN")
    board = game.board()
    output = []
    for ply, move in enumerate(game.mainline_moves(), start=1):
        before = await engine_service.candidates(board, max(100, depth * 35), 2)
        if not isinstance(before, list): before = [before]
        turn = board.turn
        best_score = before[0]["score"].pov(turn).score(mate_score=100000) or 0
        captured = board.piece_at(move.to_square) if board.is_capture(move) else None
        own = board.piece_at(move.from_square)
        is_sac = bool(own and own.piece_type in PIECE_VALUES and captured is None and board.gives_check(move))
        san = board.san(move)
        board.push(move)
        after = await engine_service.candidates(board, max(100, depth * 35), 1)
        if isinstance(after, list): after = after[0]
        actual_score = -(after["score"].pov(board.turn).score(mate_score=100000) or 0)
        label, explanation = _label(max(0, best_score - actual_score), is_sac)
        output.append({"ply": ply, "move": san, "uci": move.uci(), "evaluation": actual_score,
                       "best_move": before[0]["pv"][0].uci(), "classification": label, "explanation": explanation})
    return {"opening": identify(board), "result": game.headers.get("Result", "*"), "moves": output}
