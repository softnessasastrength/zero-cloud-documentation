import { createServer } from 'node:http';
import { mkdir, readFile, writeFile, appendFile, rename } from 'node:fs/promises';
import { dirname, resolve } from 'node:path';
import { createHash, randomUUID } from 'node:crypto';
import { fileURLToPath } from 'node:url';
import process from 'node:process';
import { log } from 'node:console';
import { setInterval } from 'node:timers';
import { applyResortCommand, initialResortState, replayResort, resortCommandSchema } from '../src/domain/resort.ts';

const dir=dirname(fileURLToPath(import.meta.url));
const dataDir=resolve(process.env.ZERO_CLOUD_DATA_DIR??resolve(dir,'../../.data'));
await mkdir(dataDir,{recursive:true});
const activePath=resolve(dataDir,'active-scenario.json');
const seeds=[20261114,20261115,20261116];
const scenarioFiles=seed=>({logPath:resolve(dataDir,`scenario-${seed}.events.jsonl`),snapshotPath:resolve(dataDir,`scenario-${seed}.snapshot.json`)});
let selectedSeed=Number(process.env.ZERO_CLOUD_SEED??20261114);
try{selectedSeed=JSON.parse(await readFile(activePath,'utf8')).seed;}catch(error){if(error.code!=='ENOENT')throw error;}
if(!seeds.includes(selectedSeed))selectedSeed=seeds[0];
let state=initialResortState(selectedSeed),commands=[];
async function loadScenario(seed){const files=scenarioFiles(seed);let entries=[];try{entries=(await readFile(files.logPath,'utf8')).split('\n').filter(Boolean).map(line=>resortCommandSchema.parse(JSON.parse(line)));}catch(error){if(error.code!=='ENOENT')throw error;}return {commands:entries,state:replayResort(seed,entries)};}
({commands,state}=await loadScenario(selectedSeed));
async function persist(command,next){const {logPath,snapshotPath}=scenarioFiles(selectedSeed);await appendFile(logPath,`${JSON.stringify(command)}\n`,'utf8');const temp=`${snapshotPath}.tmp`;await writeFile(temp,JSON.stringify(next,null,2),'utf8');await rename(temp,snapshotPath);commands.push(command);state=next;}
let writeQueue=Promise.resolve();
function commit(command){const operation=writeQueue.then(async()=>{if(state.command_ids.includes(command.id))return state;const next=applyResortCommand(state,command);await persist(command,next);return state;});writeQueue=operation.catch(()=>{});return operation;}
const respond=(res,status,body)=>{res.writeHead(status,{'content-type':'application/json; charset=utf-8'});res.end(JSON.stringify(body));};
async function body(req){let s='';for await(const chunk of req)s+=chunk;return s?JSON.parse(s):{};}
const server=createServer(async(req,res)=>{if(req.method==='OPTIONS')return respond(res,204,{});try{
 if(req.method==='GET'&&req.url==='/api/health')return respond(res,200,{ok:true,simulation:'synthetic',schema_version:1});
 if(req.method==='GET'&&req.url==='/api/scenarios')return respond(res,200,{selected_seed:selectedSeed,scenarios:[{seed:20261114,id:'resort-20261114',name:'14:00 protected break',description:'20 earned credits; Percival available.'},{seed:20261115,id:'resort-20261115',name:'36-hour entitlement',description:'Credits calculated from 36 eligible paid hours.'},{seed:20261116,id:'resort-20261116',name:'Actuator fault recovery',description:'Percival begins faulted; route coverage to Cogsworth.'}]});
 if(req.method==='GET'&&req.url==='/api/state')return respond(res,200,state);
 if(req.method==='GET'&&req.url==='/api/events')return respond(res,200,{events:state.events});
 if(req.method==='GET'&&req.url==='/api/replay'){const rebuilt=replayResort(state.seed,commands);return respond(res,200,{state:rebuilt,state_hash:createHash('sha256').update(JSON.stringify(rebuilt)).digest('hex'),commands:commands.length});}
 if(req.method==='POST'&&req.url==='/api/commands'){const raw=await body(req);const command=resortCommandSchema.parse({id:raw.id??randomUUID(),recordedAt:raw.recordedAt??new Date().toISOString(),...raw});return respond(res,200,await commit(command));}
 if(req.method==='POST'&&req.url==='/api/scenarios/select'){await writeQueue;const raw=await body(req);const seed=Number(raw.seed);if(!seeds.includes(seed))return respond(res,400,{error:'Choose one of the published deterministic scenario seeds.'});const loaded=await loadScenario(seed);selectedSeed=seed;commands=loaded.commands;state=loaded.state;const temp=`${activePath}.tmp`;await writeFile(temp,JSON.stringify({seed}), 'utf8');await rename(temp,activePath);return respond(res,200,state);}
 if(req.method==='POST'&&req.url==='/api/test/reset'&&process.env.ZERO_CLOUD_ALLOW_TEST_RESET==='1'){await writeQueue;const {logPath,snapshotPath}=scenarioFiles(selectedSeed);commands=[];state=initialResortState(selectedSeed);await writeFile(logPath,'','utf8');const temp=`${snapshotPath}.tmp`;await writeFile(temp,JSON.stringify(state,null,2),'utf8');await rename(temp,snapshotPath);return respond(res,200,state);}
 return respond(res,404,{error:'Not found'});
 }catch(error){return respond(res,400,{error:error.message??'Invalid request'});}});
const port=Number(process.env.PORT??4174);const host=process.env.HOST??'127.0.0.1';server.listen(port,host,()=>log(`ZeroCloud local simulation API listening on http://${host}:${port} (synthetic data)`));
setInterval(()=>{if(state.running){const command={id:`tick-${state.minute}-${state.events.length}`,recordedAt:new Date().toISOString(),type:'advance',minutes:state.speed};commit(resortCommandSchema.parse(command)).catch(error=>log(`Simulation clock error: ${error.message}`));}},1000).unref();
