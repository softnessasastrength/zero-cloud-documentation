import { z } from 'zod';
export type Role = 'proprietor-a' | 'proprietor-b' | 'employee' | 'engineer' | 'guest';
export type Status = 'queued' | 'preparing' | 'completed' | 'failed';
export interface Task { id:string; requestId:string; correlationId:string; title:string; resourceId:string; start:number; duration:number; dependencies:string[]; status:Status; startedAt?:number; completedAt?:number; scope:'shared'|'proprietor-a'|'proprietor-b'; approval:boolean; approved:boolean; }
export interface Clanker { id:string; name:string; role:string; location:string; battery:number; health:'healthy'|'fault'; charging:boolean; firmware:string; temperature:number; maintenance:string[]; }
export interface Telemetry { id:string; time:number; type:string; requestId:string; correlationId:string; taskId:string; resourceId:string; from:string; to:string; latency:number; quality:'simulated'; }
export interface Simulation { seed:number; rng:number; minute:number; running:boolean; speed:number; sequence:number; tasks:Task[]; fleet:Clanker[]; events:Telemetry[]; history:{minute:number;battery:number;completed:number}[]; }
export const tileSchema=z.object({id:z.string().max(80),label:z.string().min(1).max(50),route:z.string().regex(/^\/[a-z-]*$/),size:z.enum(['small','medium','wide','large']),group:z.string().min(1).max(40),color:z.string().regex(/^#[0-9a-fA-F]{6}$/),metric:z.enum(['clock','fleet','tasks','alerts','energy'])});
export type Tile=z.infer<typeof tileSchema>;
export const widgetSchema=z.object({id:z.string().max(80),title:z.string().min(1).max(60),source:z.enum(['fleet','tasks','alerts','energy','history']),width:z.enum(['normal','wide']),refresh:z.number().int().min(1).max(60)});
export const dashboardSchema=z.object({version:z.literal(1),name:z.string().min(1).max(60),widgets:z.array(widgetSchema).max(30)}).superRefine((v,c)=>{if(new Set(v.widgets.map(w=>w.id)).size!==v.widgets.length)c.addIssue({code:'custom',message:'Widget IDs must be unique'});});
export type Widget=z.infer<typeof widgetSchema>;
export type Dashboard=z.infer<typeof dashboardSchema>;
export interface Experience {location:string;atmosphere:string;lighting:string;music:string;menu:string;service:string;arrival:string;accessibility:string;staff:string;}
export const clock=(minute:number)=>`${String(Math.floor(minute/60)%24).padStart(2,'0')}:${String(minute%60).padStart(2,'0')}`;
export const parseTime=(value:string)=>{const [h,m]=value.split(':').map(Number);return h*60+m;};
