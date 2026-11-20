import type { Bot, EngineStatus } from './types'
const base = 'http://localhost:8000/api'
async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${base}${path}`, { headers: { 'Content-Type': 'application/json' }, ...init })
  if (!response.ok) throw new Error((await response.json().catch(() => null))?.detail || `Request failed (${response.status})`)
  return response.status === 204 ? undefined as T : response.json()
}
export const api = {
  health: () => request<{status: string; engine: EngineStatus}>('/health'),
  bots: () => request<Bot[]>('/bots'),
  createBot: (bot: Omit<Bot, 'id'|'created_at'>) => request<Bot>('/bots', { method:'POST', body: JSON.stringify(bot) }),
  updateBot: (id:number, bot: Omit<Bot, 'id'|'created_at'>) => request<Bot>(`/bots/${id}`, { method:'PUT', body: JSON.stringify(bot) }),
  removeBot: (id:number) => request<void>(`/bots/${id}`, { method:'DELETE' }),
  duplicateBot: (id:number) => request<Bot>(`/bots/${id}/duplicate`, { method:'POST' }),
  openings: () => request<{name:string; moves:string[]; side:string}[]>('/openings'),
  humanMove: (fen:string, move:string) => request<{fen:string;san:string;game_over:boolean;outcome:string|null}>('/position/move', { method:'POST', body:JSON.stringify({fen,move}) }),
  botMove: (fen:string, bot_id:number, time_ms=500) => request<{move:string;san:string;fen:string;info:{score:number|null;pv:string[];source:string};game_over:boolean}>('/bot/move', { method:'POST', body:JSON.stringify({fen,bot_id,time_ms}) }),
  analyze: (pgn:string, depth:number) => request<Analysis>('/analysis/game', { method:'POST', body:JSON.stringify({pgn,depth}) }),
  startEngine: (path:string) => request<EngineStatus>('/engine/start', {method:'POST',body:JSON.stringify({path})})
}
export type Analysis = {opening:string|null;result:string;moves:{ply:number;move:string;uci:string;evaluation:number;best_move:string;classification:string;explanation:string}[]}
