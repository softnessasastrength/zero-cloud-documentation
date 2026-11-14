import { beforeEach, describe, expect, it, vi } from 'vitest';
import { database } from '../src/state/store';
import { getResortOutbox, sendResortCommand, syncResortOutbox } from '../src/domain/resort-api';
import { initialResortState } from '../src/domain/resort';

describe('offline resort command outbox',()=>{
 beforeEach(async()=>{await database.settings.clear();vi.stubGlobal('crypto',{randomUUID:()=> 'queued-reservation-1'});});
 it('stores a reservation as pending and syncs it only after a receipt returns',async()=>{
  vi.stubGlobal('fetch',vi.fn().mockRejectedValue(new TypeError('offline')));
  const queued=await sendResortCommand({type:'reserve-break',employeeId:'emp-mara',guestName:'Alex',tableId:'table-garden-04',clankerId:'clanker-percival',start:840,duration:60});
  expect(queued).toEqual({queued:true});expect((await getResortOutbox())[0].status).toBe('pending');
  const committed=initialResortState();committed.reservations.push({id:'reservation-1',employee_id:'emp-mara',guest_name:'Alex',table_id:'table-garden-04',start:840,duration:60,credit_quote:12,status:'confirmed'});
  vi.stubGlobal('fetch',vi.fn().mockResolvedValue({ok:true,json:async()=>committed}));
  expect(await syncResortOutbox()).toEqual([]);expect(await getResortOutbox()).toEqual([]);
 });
 it('keeps a rejected intent visible after reconnect validation',async()=>{
  vi.stubGlobal('fetch',vi.fn().mockRejectedValueOnce(new TypeError('offline')).mockResolvedValueOnce({ok:false,status:400,json:async()=>({error:'table already reserved'})}));
  await sendResortCommand({type:'reserve-break',employeeId:'emp-mara',guestName:'Alex',tableId:'table-garden-04',clankerId:'clanker-percival',start:840,duration:60});
  const entries=await syncResortOutbox();expect(entries[0].status).toBe('rejected');expect(entries[0].message).toMatch(/already reserved/);
 });
});
