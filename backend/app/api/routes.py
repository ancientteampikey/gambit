from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import chess
import chess.pgn
from io import StringIO
from ..database import get_db
from ..models import BotProfile
from ..schemas import BotCreate, BotOut, BotUpdate, PositionRequest, MoveRequest, AnalyzeRequest, FenRequest
from ..engine.openings import OPENINGS, identify
from ..engine.service import engine_service, EngineUnavailable
from ..analysis.service import analyze_game

router = APIRouter(prefix="/api")

def get_bot_or_404(bot_id: int, db: Session):
    bot = db.get(BotProfile, bot_id)
    if not bot: raise HTTPException(404, "Bot not found")
    return bot

@router.get("/health")
async def health(): return {"status": "ok", "engine": engine_service.status()}

@router.get("/engine/status")
async def engine_status(): return engine_service.status()

@router.post("/engine/start")
async def engine_start(body: dict):
    try: return await engine_service.start(body.get("path"))
    except EngineUnavailable as exc: raise HTTPException(503, str(exc))

@router.get("/bots", response_model=list[BotOut])
def list_bots(db: Session = Depends(get_db)): return db.query(BotProfile).order_by(BotProfile.created_at.desc()).all()

@router.post("/bots", response_model=BotOut, status_code=201)
def create_bot(payload: BotCreate, db: Session = Depends(get_db)):
    if db.query(BotProfile).filter_by(name=payload.name).first(): raise HTTPException(409, "A bot with this name already exists")
    bot = BotProfile(**payload.model_dump()); db.add(bot); db.commit(); db.refresh(bot); return bot

@router.put("/bots/{bot_id}", response_model=BotOut)
def update_bot(bot_id: int, payload: BotUpdate, db: Session = Depends(get_db)):
    bot = get_bot_or_404(bot_id, db)
    for key, value in payload.model_dump().items(): setattr(bot, key, value)
    db.commit(); db.refresh(bot); return bot

@router.post("/bots/{bot_id}/duplicate", response_model=BotOut, status_code=201)
def duplicate_bot(bot_id: int, db: Session = Depends(get_db)):
    bot = get_bot_or_404(bot_id, db)
    base, suffix = f"{bot.name} Copy", 2
    name = base
    while db.query(BotProfile).filter_by(name=name).first():
        name, suffix = f"{base} {suffix}", suffix + 1
    copy = BotProfile(name=name, opening=bot.opening, style=bot.style, elo=bot.elo, risk=bot.risk, color=bot.color)
    db.add(copy); db.commit(); db.refresh(copy); return copy

@router.delete("/bots/{bot_id}", status_code=204)
def delete_bot(bot_id: int, db: Session = Depends(get_db)):
    db.delete(get_bot_or_404(bot_id, db)); db.commit()

@router.get("/openings")
def openings(): return [{"name": x.name, "moves": list(x.moves), "side": "white" if x.side else "black"} for x in OPENINGS]

@router.post("/position/validate")
def validate_fen(payload: FenRequest):
    try:
        board = chess.Board(payload.fen)
        return {"valid": True, "fen": board.fen(), "opening": identify(board), "legal_moves": [m.uci() for m in board.legal_moves]}
    except ValueError as exc: raise HTTPException(422, f"Invalid FEN: {exc}")

@router.post("/position/move")
def play_move(payload: MoveRequest):
    try:
        board = chess.Board(payload.fen); move = chess.Move.from_uci(payload.move)
        if move not in board.legal_moves: raise HTTPException(422, "Illegal move")
        san = board.san(move); board.push(move)
        return {"fen": board.fen(), "san": san, "game_over": board.is_game_over(), "outcome": board.outcome().result() if board.outcome() else None}
    except ValueError as exc: raise HTTPException(422, f"Invalid position or move: {exc}")

@router.post("/bot/move")
async def bot_move(payload: PositionRequest, db: Session = Depends(get_db)):
    try: board = chess.Board(payload.fen)
    except ValueError as exc: raise HTTPException(422, f"Invalid FEN: {exc}")
    bot = get_bot_or_404(payload.bot_id, db) if payload.bot_id else BotProfile(name="Gambit", style="balanced", elo=1500, risk=50, opening="Any", color="random")
    try:
        move, info = await engine_service.choose_move(board, bot, payload.time_ms)
        san = board.san(move); board.push(move)
        return {"move": move.uci(), "san": san, "fen": board.fen(), "info": info, "game_over": board.is_game_over()}
    except EngineUnavailable as exc: raise HTTPException(503, str(exc))

@router.post("/analysis/game")
async def analysis(payload: AnalyzeRequest):
    try: return await analyze_game(payload.pgn, payload.depth)
    except EngineUnavailable as exc: raise HTTPException(503, str(exc))
    except ValueError as exc: raise HTTPException(422, str(exc))

@router.post("/pgn/validate")
def pgn_validate(body: dict):
    game = chess.pgn.read_game(StringIO(body.get("pgn", "")))
    if not game: raise HTTPException(422, "Invalid PGN")
    return {"valid": True, "moves": len(list(game.mainline_moves())), "headers": dict(game.headers)}
