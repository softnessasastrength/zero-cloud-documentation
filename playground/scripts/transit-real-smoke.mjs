import { spawn, spawnSync } from 'node:child_process';
import { mkdtemp, mkdir, rm, writeFile } from 'node:fs/promises';
import { tmpdir } from 'node:os';
import path from 'node:path';
import process from 'node:process';
import assert from 'node:assert/strict';
import { chromium } from '@playwright/test';
const store=await mkdtemp(path.join(tmpdir(),'percival-real-browser-'));
const transit=path.resolve('../transit');
const imported=spawnSync('python3',['-m','percival_transit','--store',store,'import','--accept-source-terms'],{cwd:transit,encoding:'utf8'});
if(imported.status!==0)throw Error(imported.stdout+imported.stderr);
const metadata=JSON.parse(imported.stdout);
const api=spawn('python3',['-m','percival_transit','--store',store,'serve','--port','8766'],{cwd:transit,stdio:'ignore'});
const web=spawn(process.execPath,['node_modules/vite/bin/vite.js','preview','--host','127.0.0.1','--port','4184','--strictPort'],{env:{...process.env,PERCIVAL_TRANSIT_PORT:'8766'},stdio:'ignore'});
let browser;
try{
 for(let n=0;n<100;n++){try{const r=await fetch('http://127.0.0.1:4184/transit-api/v1/health');if(r.ok)break;}catch{}await new Promise(r=>setTimeout(r,100));}
 browser=await chromium.launch();const page=await browser.newPage({viewport:{width:1366,height:1000}});
 await page.goto('http://127.0.0.1:4184/#/transit');
 await page.getByLabel('Query date/time (blank = now)').fill('2026-11-13T05:00:00-05:00');
 await page.getByRole('button',{name:'Check departures'}).click();
 const evidence={snapshot:metadata.snapshot,snapshot_date:metadata.fetched_at,source:metadata.source,query_at:'2026-11-13T05:00:00-05:00',boards:{}};
 for(const [name,time,stop] of [['Hartford Union Station','6:45 AM','6'],['Windsor Locks','10:44 AM','8']]){
   const region=page.getByRole('region',{name,exact:true});
   await region.getByText(new RegExp(time)).first().waitFor();
   const text=await region.innerText();assert(!text.includes('DEMO DATA'));assert(text.includes('Scheduled'));assert(text.includes('Service date 2026-11-13'));
   await region.getByText('Feed provenance',{exact:true}).click();
   assert((await region.innerText()).includes('Source stops: '+stop));
   evidence.boards[name]={status:'Scheduled',stop_id:stop,sample:time,service_date:'2026-11-13'};
 }
 await mkdir('test-results',{recursive:true});
 await page.getByRole('region',{name:'Hartford Union Station',exact:true}).scrollIntoViewIfNeeded();
 await page.screenshot({path:'test-results/real-transit.png'});
 await writeFile('test-results/real-transit.json',JSON.stringify(evidence,null,2));
 console.log('REAL_METRO_EVIDENCE '+JSON.stringify(evidence));
}finally{await browser?.close();api.kill('SIGTERM');web.kill('SIGTERM');await Promise.all([new Promise(r=>api.once('exit',r)),new Promise(r=>web.once('exit',r))]);await rm(store,{recursive:true,force:true});}
