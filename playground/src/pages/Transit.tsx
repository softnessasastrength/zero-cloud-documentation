import { BusTransit } from './TransitBus';
import { useEffect, useState } from 'react';
import { Link, useParams } from 'react-router-dom';
import { getBoard, stationNames, transitTime, type Board } from '../domain/transit-api';
function useBoard(station: string, at = '', refresh = 0) {
  const [board, setBoard] = useState<Board>();
  useEffect(() => { let active = true; const update = () => { void getBoard(station, at).then(result => { if (active) setBoard(result); }); }; update(); const timer = setInterval(update, 60000); return () => { active = false; clearInterval(timer); }; }, [station, at, refresh]);
  return board;
}
export function TransitTiles() {
  return <section className="transit-tiles" aria-label="Transit tiles"><Link className="transit-tile" to="/transit"><small>PERSONAL MOBILITY</small><strong>Transit</strong><span>Hartford Line · scheduled</span></Link>{Object.entries(stationNames).map(([id, name]) => <PinnedStation key={id} id={id} name={name} />)}</section>;
}
function PinnedStation({ id, name }: { id: string; name: string }) {
  const board = useBoard(id); const next = board?.departures.find(d => Date.parse(d.departure) >= Date.now());
  return <Link className="transit-tile" to={'/transit/' + id}><small>{board?.fixture ? 'DEMO DATA · ' : ''}{board?.cached ? 'CACHED · ' : ''}{board?.status ?? 'Checking…'}</small><strong>{name}</strong><span>{next ? transitTime(next.departure) : board?.status === 'Scheduled' ? 'No departures in this window' : 'Open station board'}</span>{board?.snapshot_date && <small>Snapshot {transitTime(board.snapshot_date)}</small>}</Link>;
}
function StationBoard({ station, at, refresh }: { station: string; at: string; refresh: number }) {
  const board = useBoard(station, at, refresh);
  return <BoardPanel board={board} title={stationNames[station]}/>;
}
export function BoardPanel({board,title}:{board:Board|undefined;title:string}) {
  return <section className="metro-panel transit-board" aria-label={title}><h2>{title}</h2>{!board ? <p role="status">Checking local schedule…</p> : <>
    <p className="transit-state">{board.fixture && <strong>DEMO DATA — FICTIONAL SERVICE · </strong>}{board.cached && <strong>CACHED · </strong>}{board.status}</p><p>{board.reason}</p>
    {board.cached && <p>Saved query as of {transitTime(board.checked_at)}. These are historical cached results. New queries require the local service.</p>}
    <p>Snapshot: {board.snapshot_date ? transitTime(board.snapshot_date) : 'unavailable'} · Age: {board.snapshot_date ? `${Math.max(0, Math.floor((Date.now() - Date.parse(board.snapshot_date)) / 3600000))} hours` : 'Unknown'}</p>
    <p>Feed coverage: {board.coverage_start ?? 'Unknown'} → {board.coverage_end ?? 'Unknown'} · Times: America/New_York</p>{board.verified_coverage_end&&<p>Reconciled published timetable through {board.verified_coverage_end}; later dates need a verified update.</p>}
    {board.status === 'Scheduled' && !board.departures.length && <p className="transit-empty">No scheduled departures in this covered 24-hour query window. This is not a missing-feed result.</p>}
    <ol className="departure-list">{board.departures.slice(0,6).map(d => <li key={`${d.source_trip_id}:${d.service_date}:${d.source_stop_id}`}><strong>{transitTime(d.departure)}</strong><span>{d.destination || d.headsign || 'Destination not supplied'} · Scheduled</span><span>{d.route_label && `${d.route_label} · `}{d.headsign}<br/>Trip {d.train_number || d.source_trip_id} · Service date {d.service_date}</span>{d.route_label==='G5'&&d.downstream_stop_names&&<span>{d.downstream_stop_names.some(n=>/massmutual|mass mutual|bright meadow/i.test(n))?'Continues to Bright Meadow':'Does not continue to Bright Meadow on this trip'}</span>}<details><summary>Source record</summary><p>Trip {d.source_trip_id} · Stop {d.source_stop_id} · Direction {d.direction_id ?? 'not supplied'}</p><code>{d.snapshot}</code></details></li>)}</ol>
    <p>Showing the next {Math.min(6,board.departures.length)} of {board.departures.length} scheduled events in this query window.</p><details><summary>Feed provenance</summary><p>{board.source ?? 'No source available'}</p><code>{board.snapshot}</code><p>Source stops: {board.source_stop_ids?.join(', ') ?? 'Unknown'} · Query starts {board.queried_at || 'now'}</p></details>
  </>}</section>;
}
export function Transit() {
  const { station } = useParams(); const [input, setInput] = useState(''); const [at, setAt] = useState(''); const [refresh, setRefresh] = useState(0); const [error, setError] = useState('');
  const stations = station && stationNames[station] ? [station] : Object.keys(stationNames);
  return <div className="transit-page"><header><span className="eyebrow">PERCIVAL · PERSONAL MOBILITY</span><h1>Transit</h1><p>Hartford Line scheduled departures. Timetables do not verify operation, delays, cancellations, or a return journey.</p><nav aria-label="Transit stations"><Link to="/transit">Both boards</Link>{Object.entries(stationNames).map(([id, name]) => <Link key={id} to={'/transit/' + id}>{name}</Link>)}<Link to="/resort">Resort simulator</Link></nav></header>
    <form className="editor-bar" onSubmit={e => { e.preventDefault(); if (input && (!Number.isFinite(Date.parse(input)) || !/(Z|[+-]\d\d:\d\d)$/.test(input))) { setError('Enter a complete ISO date/time including UTC offset, or leave blank for now.'); return; } setError(''); setAt(input); setRefresh(n => n + 1); }}><label>Query date/time (blank = now)<input placeholder="2026-11-13T05:00:00-05:00" value={input} onChange={e => setInput(e.target.value)} /></label><button type="submit">Check departures</button>{error && <p role="alert">{error}</p>}</form>
    <BusTransit at={at} refresh={refresh}/><div className="transit-boards">{stations.map(id => <StationBoard key={id} station={id} at={at} refresh={refresh} />)}</div></div>;
}
