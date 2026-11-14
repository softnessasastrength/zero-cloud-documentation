import { describe,it,expect } from 'vitest';
import { advance,submit,fault,visibleEvents } from '../src/domain/engine';
import { createSimulation } from '../src/domain/seed';
const request={title:'Coffee',resourceId:'pennington',start:391,duration:5,dependencies:[],scope:'shared' as const,approval:false,approved:false};
describe('deterministic execution',()=>{
it('does not complete before execution and produces correlated completion',()=>{const s=submit(createSimulation(),request,'proprietor-a');expect(s.tasks[0].status).toBe('queued');expect(advance(s,5).tasks[0].status).toBe('preparing');const result=advance(s,6);expect(result.tasks[0].status).toBe('completed');expect(result.events.at(-1)?.requestId).toBe(result.tasks[0].requestId);expect(result).toEqual(advance(s,6));});
it('blocks conflicting reservations and unauthorized dispatch',()=>{const s=submit(createSimulation(),request,'engineer');expect(()=>submit(s,request,'engineer')).toThrow(/conflict/);expect(()=>submit(s,request,'guest')).toThrow(/Guest/);});
it('holds approval and fails active work on fault',()=>{const pending=submit(createSimulation(),{...request,approval:true},'proprietor-a');expect(advance(pending,20).tasks[0].status).toBe('queued');const active=advance(submit(createSimulation(),request,'engineer'),1);expect(advance(fault(active,'pennington','engineer'),1).tasks[0].status).toBe('failed');});
it('hides private traces from other roles',()=>{const s=submit(createSimulation(),{...request,scope:'proprietor-a'},'proprietor-a');expect(visibleEvents(s,'proprietor-b')).toEqual([]);expect(visibleEvents(s,'proprietor-a')).toHaveLength(1);});
it('waits for dependencies',()=>{let s=submit(createSimulation(),request,'engineer');s=submit(s,{...request,resourceId:'percival',dependencies:[s.tasks[0].id]},'engineer');expect(advance(s,2).tasks[1].status).toBe('queued');expect(advance(s,6).tasks[1].status).toBe('preparing');});
});
