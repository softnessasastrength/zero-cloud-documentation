export type Departure = { departure: string; headsign: string; destination?: string; direction_id?: string; train_number?: string; route_label?: string; source_trip_id: string; source_stop_id: string; service_date: string; snapshot: string; fixture: boolean; downstream_stop_ids?: string[]; downstream_stop_names?: string[] };
export type Board = { api_version: string; status: string; station: string; reason: string; queried_at: string; checked_at: string; snapshot?: string; snapshot_date?: string; source_checked_at?: string; coverage_start?: string; coverage_end?: string; verified_coverage_end?: string; source?: string; fixture?: boolean; source_stop_ids?: string[]; departures: Departure[]; cached?: boolean };
export const stationNames: Record<string, string> = { hartford: 'Hartford Union Station', 'windsor-locks': 'Windsor Locks' };
export const transitTime = (value: string) => new Date(value).toLocaleString('en-US', { timeZone: 'America/New_York', month: 'short', day: 'numeric', hour: 'numeric', minute: '2-digit', timeZoneName: 'short' });
export function cachedBoard(value: Board, now = Date.now()): Board {
  const age = (value.source_checked_at || value.snapshot_date) ? now - Date.parse(value.source_checked_at || value.snapshot_date || '') : Infinity;
  if (!Number.isFinite(age) || !Number.isFinite(Date.parse(value.queried_at)) || age > 7 * 86400000 || age < 0 || now >= Date.parse(value.queried_at) + 24 * 3600000) return { ...value, cached: true, status: 'Unknown', departures: [], reason: 'Cached snapshot or query window has expired. Start the local Transit service to refresh.' };
  return { ...value, cached: true };
}
export async function getBoard(station: string, at = ''): Promise<Board> {
  const path = `/transit-api/v1/stations/${station}/departures${at ? `?at=${encodeURIComponent(at)}` : ''}`;
  return getTransitBoard(path,station,at);
}
export async function getTransitBoard(path:string, station:string, at=''):Promise<Board>{
  const key = 'percival-transit-v1:' + path;
  try {
    const response = await fetch(path, { cache: 'no-store', signal: AbortSignal.timeout(8000) });
    const body = await response.json() as Board;
    if (body.api_version !== 'v1' || !Array.isArray(body.departures) || !['Scheduled', 'Unknown'].includes(body.status)) throw new Error('Invalid Transit service response');
    try { localStorage.setItem(key, JSON.stringify(body)); } catch { /* Cache is optional. */ }
    return body;
  } catch {
    try { const stored = localStorage.getItem(key); if (stored) return cachedBoard(JSON.parse(stored) as Board); } catch { /* Broken cache is missing evidence. */ }
    return { api_version: 'v1', station, status: 'Unknown', reason: 'The local Transit service is unavailable. A new query requires the service; no cached result matches this query.', departures: [], queried_at: at, checked_at: new Date().toISOString() };
  }
}
