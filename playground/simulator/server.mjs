import { createServer } from 'node:http';
import { mkdir, readFile, writeFile, appendFile, rename } from 'node:fs/promises';
import { dirname, resolve } from 'node:path';
import { createHash, randomUUID } from 'node:crypto';
import { fileURLToPath } from 'node:url';
import process from 'node:process';
import { log } from 'node:console';
import { applyResortCommand, initialResortState, replayResort, resortCommandSchema } from '../src/domain/resort.ts';

const dir=dirname(fileURLToPath(import.meta.url));
const dataDir=resolve(process.env.ZERO_CLOUD_DATA_DIR??resolve(dir,'../../.data'));
const logPath=resolve(dataDir,'events.jsonl');
const snapshotPath=resolve(dataDir,'snapshot.json');
await mkdir(dataDir,{recursive:true});
let state=initialResortState(Number(process.env.ZERO_CLOUD_SEED??20261114));
let commands=[];
try { commands=(await readFile(logPath,'utf8')).split('\n').filter(Boolean).map(line=>resortCommandSchema.parse(JSON.parse(line)));state=replayResort(state.seed,commands); }
catch(error){if(error.code!=='ENOENT')throw error;}
async function persist(command,next){await appendFile(logPath,`${JSON.stringify(command)}\n`,'utf8');const temp=`${snapshotPath}.tmp`;await writeFile(temp,JSON.stringify(next,null,2),'utf8');await rename(temp,snapshotPath);commands.push(command);state=next;}
const respond=(res,status,body)=>{res.writeHead(status,{'content-type':'application/json; charset=utf-8','access-control-allow-origin':'*','access-control-allow-methods':'GET,POST,OPTIONS','access-control-allow-headers':'content-type'});res.end(JSON.stringify(body));};
async function body(req){let s='';for await(const chunk of req)s+=chunk;return s?JSON.parse(s):{};}
const server=createServer(async(req,res)=>{if(req.method==='OPTIONS')return respond(res,204,{});try{
 if(req.method==='GET'&&req.url==='/api/health')return respond(res,200,{ok:true,simulation:'synthetic',schema_version:1});
 if(req.method==='GET'&&req.url==='/api/state')return respond(res,200,state);
 if(req.method==='GET'&&req.url==='/api/events')return respond(res,200,{events:state.events});
 if(req.method==='GET'&&req.url==='/api/replay'){const rebuilt=replayResort(state.seed,commands);return respond(res,200,{state:rebuilt,state_hash:createHash('sha256').update(JSON.stringify(rebuilt)).digest('hex'),commands:commands.length});}
 if(req.method==='POST'&&req.url==='/api/commands'){const raw=await body(req);const command=resortCommandSchema.parse({id:raw.id??randomUUID(),recordedAt:raw.recordedAt??new Date().toISOString(),...raw});if(state.command_ids.includes(command.id))return respond(res,200,state);const next=applyResortCommand(state,command);await persist(command,next);return respond(res,200,state);}
 return respond(res,404,{error:'Not found'});
 }catch(error){return respond(res,400,{error:error.message??'Invalid request'});}});
const port=Number(process.env.PORT??4174);const host=process.env.HOST??'127.0.0.1';server.listen(port,host,()=>log(`ZeroCloud local simulation API listening on http://${host}:${port} (synthetic data)`));
