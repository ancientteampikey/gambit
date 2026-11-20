from dataclasses import dataclass
import chess

@dataclass(frozen=True)
class Opening:
    name: str
    moves: tuple[str, ...]
    side: chess.Color | None = None

OPENINGS = [
    Opening("Caro-Kann Defense", ("e2e4", "c7c6"), chess.BLACK),
    Opening("Sicilian Defense", ("e2e4", "c7c5"), chess.BLACK),
    Opening("French Defense", ("e2e4", "e7e6"), chess.BLACK),
    Opening("Scandinavian Defense", ("e2e4", "d7d5"), chess.BLACK),
    Opening("Pirc Defense", ("e2e4", "d7d6", "d2d4", "g8f6"), chess.BLACK),
    Opening("King's Indian Defense", ("d2d4", "g8f6", "c2c4", "g7g6"), chess.BLACK),
    Opening("Queen's Gambit", ("d2d4", "d7d5", "c2c4"), chess.WHITE),
    Opening("Queen's Pawn Game", ("d2d4",), chess.WHITE),
    Opening("London System", ("d2d4", "d7d5", "g1f3", "g8f6", "c1f4"), chess.WHITE),
    Opening("King's Gambit", ("e2e4", "e7e5", "f2f4"), chess.WHITE),
    Opening("Italian Game", ("e2e4", "e7e5", "g1f3", "b8c6", "f1c4"), chess.WHITE),
    Opening("Ruy Lopez", ("e2e4", "e7e5", "g1f3", "b8c6", "f1b5"), chess.WHITE),
    Opening("English Opening", ("c2c4",), chess.WHITE),
    Opening("Réti Opening", ("g1f3",), chess.WHITE),
    Opening("Nimzo-Indian Defense", ("d2d4", "g8f6", "c2c4", "e7e6", "b1c3", "f8b4"), chess.BLACK),
    Opening("Slav Defense", ("d2d4", "d7d5", "c2c4", "c7c6"), chess.BLACK),
    Opening("Dutch Defense", ("d2d4", "f7f5"), chess.BLACK),
]

def identify(board: chess.Board) -> str | None:
    history = tuple(move.uci() for move in board.move_stack)
    candidates = [opening for opening in OPENINGS if history[:len(opening.moves)] == opening.moves]
    return max(candidates, key=lambda x: len(x.moves)).name if candidates else None

def repertoire_move(board: chess.Board, selected: str, bot_color: chess.Color) -> chess.Move | None:
    if selected == "Any" or board.turn != bot_color:
        return None
    opening = next((x for x in OPENINGS if x.name == selected), None)
    if not opening or (opening.side is not None and opening.side != bot_color):
        return None
    index = len(board.move_stack)
    if index >= len(opening.moves):
        return None
    try:
        move = chess.Move.from_uci(opening.moves[index])
        return move if move in board.legal_moves else None
    except ValueError:
        return None
