import { describe, expect, it } from 'vitest';
import { applyResortCommand, initialResortState, replayResort, type ResortCommand } from '../src/domain/resort';

const at=(id:string,type:ResortCommand['type'],extra:Record<string,unknown>={}):ResortCommand=>({id,recordedAt:'2026-11-14T13:00:00.000Z',type,...extra} as ResortCommand);
describe('event-sourced resort simulator',()=>{
 it('accrues credits at 0.5 per eligible paid hour and atomically confirms a protected break scenario',()=>{
  let s=initialResortState(11);expect(s.employees[0].credit_balance).toBe(s.employees[0].paid_hours*.5);
  s=applyResortCommand(s,at('book-1','reserve-break',{employeeId:'emp-mara',guestName:'Alex',tableId:'table-garden-04',clankerId:'clanker-percival',start:840,duration:60}));
  expect(s.reservations).toHaveLength(1);expect(s.employees[0].credit_balance).toBe(8);expect(s.employees[0].protected_from).toBe(840);expect(s.clankers[0].status).toBe('dispatched');
  expect(s.events.map(e=>e.event_type)).toEqual(expect.arrayContaining(['restaurant.reservation.confirmed','zeropay.credit.redeemed','workforce.break.protected','clanker.dispatch.accepted']));
 });
 it('rejects a reservation without mutating its input when table, credit, or fleet constraints fail',()=>{
  const initial=initialResortState();const booked=applyResortCommand(initial,at('book-1','reserve-break',{employeeId:'emp-mara',guestName:'Alex',tableId:'table-garden-04',clankerId:'clanker-percival',start:840,duration:60}));
  const anotherEmployee=structuredClone(booked);anotherEmployee.employees.push({id:'emp-jo',name:'Jo Vale',role:'Server',paid_hours:40,credit_balance:20,status:'on-duty'});
  expect(()=>applyResortCommand(anotherEmployee,at('book-2','reserve-break',{employeeId:'emp-jo',guestName:'Jo',tableId:'table-garden-04',clankerId:'clanker-cogsworth',start:850,duration:45}))).toThrow(/already reserved/);
  expect(initial.reservations).toHaveLength(0);expect(initial.employees[0].credit_balance).toBe(20);
 });
 it('is idempotent by command id and replay has the same state hash input',()=>{
  const cmds=[at('book-1','reserve-break',{employeeId:'emp-mara',guestName:'Alex',tableId:'table-garden-04',clankerId:'clanker-percival',start:840,duration:60}),at('advance-1','advance',{minutes:60})];
  const once=replayResort(42,cmds), duplicate=applyResortCommand(once,cmds[1]);expect(duplicate).toEqual(once);expect(replayResort(42,cmds)).toEqual(once);
  expect(once.employees[0].status).toBe('on-break');expect(once.events.some(e=>e.event_type==='workforce.break.started')).toBe(true);expect(once.clankers[0].assignment_started).toBe(true);
  const complete=applyResortCommand(once,at('advance-2','advance',{minutes:60}));expect(complete.employees[0].status).toBe('on-duty');expect(complete.clankers[0].status).toBe('available');expect(complete.clankers[0].battery).toBe(80);
 });
 it('records clock speed and rejects unsafe or unauthorized fault injection',()=>{
  const speed=applyResortCommand(initialResortState(),at('speed-1','set-speed',{speed:15}));expect(speed.speed).toBe(15);
  expect(()=>applyResortCommand(speed,at('fault-1','fault',{clankerId:'clanker-percival',operation:'inject',actorRole:'guest'}))).toThrow();
  const faulted=applyResortCommand(speed,at('fault-2','fault',{clankerId:'clanker-percival',operation:'inject',actorRole:'engineer'}));expect(faulted.clankers[0].status).toBe('fault');
  expect(()=>applyResortCommand(faulted,at('book-1','reserve-break',{employeeId:'emp-mara',guestName:'Alex',tableId:'table-garden-04',clankerId:'clanker-percival',start:840,duration:60}))).toThrow(/No eligible clanker/);
 });
});
