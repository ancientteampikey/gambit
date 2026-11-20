import chess
from fastapi.testclient import TestClient
from app.main import app
from app.engine.openings import identify, repertoire_move

def moves(sequence):
    board = chess.Board()
    for uci in sequence:
        board.push_uci(uci)
    return board

def test_identifies_caro_kann():
    board = moves(["e2e4", "c7c6"])
    assert identify(board) == "Caro-Kann Defense"

def test_repertoire_respects_colour_and_legality():
    board = moves(["e2e4"])
    assert repertoire_move(board, "Caro-Kann Defense", chess.BLACK) == chess.Move.from_uci("c7c6")
    assert repertoire_move(board, "Caro-Kann Defense", chess.WHITE) is None

def test_checkmate_and_stalemate_are_reported_by_chess_core():
    checkmate = moves(["f2f3", "e7e5", "g2g4", "d8h4"])
    assert checkmate.is_checkmate()
    stalemate = chess.Board("7k/5Q2/7K/8/8/8/8/8 b - - 0 1")
    assert stalemate.is_stalemate()

def test_api_validates_moves_on_the_backend():
    with TestClient(app) as client:
        response = client.post("/api/position/move", json={"fen": chess.STARTING_FEN, "move": "e2e4"})
    assert response.status_code == 200
    assert response.json()["san"] == "e4"

def test_api_rejects_an_illegal_move():
    with TestClient(app) as client:
        response = client.post("/api/position/move", json={"fen": chess.STARTING_FEN, "move": "e2e5"})
    assert response.status_code == 422
