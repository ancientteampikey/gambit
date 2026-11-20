# Build a self-contained public GAMBIT web service.
FROM node:24-alpine AS frontend
WORKDIR /build/frontend
COPY frontend/package*.json ./
RUN npm ci --no-audit --no-fund
COPY frontend/ ./
RUN npm run build

FROM debian:bookworm-slim AS stockfish
RUN apt-get update && apt-get install -y --no-install-recommends g++ make curl ca-certificates && rm -rf /var/lib/apt/lists/*
WORKDIR /build/stockfish
COPY stockfish/Stockfish-master/ ./Stockfish-master/
WORKDIR /build/stockfish/Stockfish-master/src
# SSE4.1 is broadly available on modern cloud x86 servers; do not assume AVX2.
RUN make -j2 build ARCH=x86-64-sse41-popcnt && cp stockfish /opt/stockfish

FROM python:3.13-slim
WORKDIR /app
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 GAMBIT_STOCKFISH_PATH=/opt/stockfish
COPY backend/requirements.txt ./backend/requirements.txt
RUN pip install --no-cache-dir -r backend/requirements.txt
COPY backend/ ./backend/
COPY --from=frontend /build/frontend/dist ./backend/app/web
COPY --from=stockfish /opt/stockfish /opt/stockfish
RUN mkdir -p /app/data
EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--app-dir", "backend", "--host", "0.0.0.0", "--port", "8000"]
