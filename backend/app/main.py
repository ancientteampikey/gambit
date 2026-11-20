from contextlib import asynccontextmanager
from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from .database import Base, engine
from .api.routes import router
from .engine.service import engine_service

@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    await engine_service.start()
    yield
    await engine_service.close()

app = FastAPI(title="GAMBIT Chess Engine", version="0.1.0", lifespan=lifespan)
app.add_middleware(CORSMiddleware, allow_origins=["http://localhost:5173"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])
app.include_router(router)

# In production Docker builds, the compiled React app is copied here and
# served by the same process as the API. Vite remains the development server.
web_dir = Path(__file__).parent / "web"
if web_dir.is_dir():
    app.mount("/", StaticFiles(directory=web_dir, html=True), name="web")
