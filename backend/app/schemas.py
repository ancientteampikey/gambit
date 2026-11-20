from datetime import datetime
from pydantic import BaseModel, Field

class BotBase(BaseModel):
    name: str = Field(min_length=1, max_length=80)
    opening: str = "Any"
    style: str = "balanced"
    elo: int = Field(default=1500, ge=400, le=3000)
    risk: int = Field(default=50, ge=0, le=100)
    color: str = "random"

class BotCreate(BotBase): pass
class BotUpdate(BotBase): pass

class BotOut(BotBase):
    id: int
    created_at: datetime
    model_config = {"from_attributes": True}

class PositionRequest(BaseModel):
    fen: str
    bot_id: int | None = None
    time_ms: int = Field(default=500, ge=50, le=10000)

class MoveRequest(BaseModel):
    fen: str
    move: str

class AnalyzeRequest(BaseModel):
    pgn: str = Field(min_length=1)
    depth: int = Field(default=14, ge=6, le=24)

class FenRequest(BaseModel):
    fen: str
