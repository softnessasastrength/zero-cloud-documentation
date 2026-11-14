import { afterEach, expect, it, vi } from 'vitest';
import { cleanup, render, screen } from '@testing-library/react';
import { cachedBoard, getBoard, type Board } from '../src/domain/transit-api';
import { BoardPanel } from '../src/pages/Transit';
const board:Board={api_version:'v1',status:'Scheduled',station:'hartford',reason:'Timetable only',queried_at:'2026-11-14T12:00:00Z',checked_at:'2026-11-14T12:00:00Z',snapshot_date:'2026-11-14T12:00:00Z',fixture:true,departures:[]};
afterEach(()=>{cleanup();localStorage.clear();vi.restoreAllMocks();});
it('distinguishes covered empty boards from missing data and labels fixtures',()=>{render(<BoardPanel board={board} title="Hartford Union Station"/>);expect(screen.getByText(/No scheduled departures in this covered/)).toBeDefined();expect(screen.getByText(/DEMO DATA/)).toBeDefined();cleanup();render(<BoardPanel board={{...board,status:'Unknown',reason:'missing feed'}} title="Windsor Locks"/>);expect(screen.getByText('missing feed')).toBeDefined();expect(screen.queryByText(/No scheduled departures in this covered/)).toBeNull();});
it('expires cached snapshots and cached query windows',()=>{expect(cachedBoard(board,Date.parse('2026-11-14T13:00:00Z')).status).toBe('Scheduled');expect(cachedBoard(board,Date.parse('2026-11-15T13:00:00Z')).status).toBe('Unknown');expect(cachedBoard(board,Date.parse('2026-11-24T13:00:00Z')).departures).toEqual([]);});
it('never reuses another query when local service is down',async()=>{vi.spyOn(globalThis,'fetch').mockRejectedValue(new Error('offline'));const result=await getBoard('hartford','2026-11-20T12:00:00Z');expect(result.status).toBe('Unknown');expect(result.departures).toEqual([]);});
