import type { ResortCommand, ResortState } from './resort';
import { database } from '../state/store';

type CommandInput=ResortCommand extends infer C?C extends {id:string;recordedAt:string}?Omit<C,'id'|'recordedAt'>:never:never;
export interface ResortScenario {seed:number;id:string;name:string;description:string;}
export interface OutboxEntry {command:Extract<ResortCommand,{type:'reserve-break'}>;status:'pending'|'rejected';message?:string;}
const STATE_KEY='resort-state-cache-v1',OUTBOX_KEY='resort-command-outbox-v1';
async function request<T>(path:string,init?:RequestInit):Promise<T>{const response=await fetch(`/api/${path}`,{headers:{'content-type':'application/json',...init?.headers},...init});const result=await response.json() as T&{error?:string};if(!response.ok)throw new Error(result.error??`Local API returned ${response.status}.`);return result;}
async function cachedState(){const row=await database.settings.get(STATE_KEY);return row?JSON.parse(row.value) as ResortState:undefined;}
async function cacheState(state:ResortState){await database.settings.put({key:STATE_KEY,value:JSON.stringify(state)});}
async function readOutbox():Promise<OutboxEntry[]>{const row=await database.settings.get(OUTBOX_KEY);return row?JSON.parse(row.value) as OutboxEntry[]:[];}
async function writeOutbox(entries:OutboxEntry[]){await database.settings.put({key:OUTBOX_KEY,value:JSON.stringify(entries)});}
export async function getResortSnapshot():Promise<{state:ResortState;stale:boolean}>{try{const state=await request<ResortState>('state');await cacheState(state);return {state,stale:false};}catch(error){const cached=await cachedState();if(cached&&error instanceof TypeError)return {state:cached,stale:true};throw error;}}
export const getResortState=async()=> (await getResortSnapshot()).state;
export const getResortScenarios=()=>request<{selected_seed:number;scenarios:ResortScenario[]}>('scenarios');
export const selectResortScenario=async(seed:number)=>{const state=await request<ResortState>('scenarios/select',{method:'POST',body:JSON.stringify({seed})});await cacheState(state);return state;};
export const getResortReplay=()=>request<{state:ResortState;state_hash:string;commands:number}>('replay');
export const getResortOutbox=readOutbox;
export async function discardOutboxCommand(id:string){await writeOutbox((await readOutbox()).filter(entry=>entry.command.id!==id));}
export async function sendResortCommand(input:CommandInput):Promise<{state:ResortState}|{queued:true}>{const command={...input,id:crypto.randomUUID(),recordedAt:new Date().toISOString()} as ResortCommand;try{const state=await request<ResortState>('commands',{method:'POST',body:JSON.stringify(command)});await cacheState(state);return {state};}catch(error){if(!(error instanceof TypeError)||command.type!=='reserve-break')throw error;const entries=await readOutbox();entries.push({command,status:'pending'});await writeOutbox(entries);return {queued:true};}}
export async function syncResortOutbox(){const entries=await readOutbox();let changed=false;for(let i=0;i<entries.length;i++){const entry=entries[i];if(entry.status!=='pending')continue;try{const state=await request<ResortState>('commands',{method:'POST',body:JSON.stringify(entry.command)});await cacheState(state);entries.splice(i,1);i--;changed=true;}catch(error){if(error instanceof TypeError)break;entries[i]={...entry,status:'rejected',message:(error as Error).message};changed=true;}}if(changed)await writeOutbox(entries);return entries;}
