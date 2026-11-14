import { spawn } from 'node:child_process';
import process from 'node:process';
import assert from 'node:assert/strict';
const {fetch,setTimeout,console}=globalThis;
const cwd=process.cwd(),apiPort=4174,webPort=4200+Math.floor(Math.random()*30000),base=`http://127.0.0.1:${webPort}`;
const api=spawn(process.execPath,['--import','tsx','./simulator/server.mjs'],{cwd,env:{...process.env,PORT:String(apiPort),ZERO_CLOUD_DATA_DIR:'.data-pwa-smoke'},stdio:'ignore'});
const web=spawn(process.execPath,['./node_modules/vite/bin/vite.js','preview','--host','127.0.0.1','--port',String(webPort),'--strictPort'],{cwd,stdio:'ignore'});
async function ready(url){for(let i=0;i<60;i++){try{const r=await fetch(url);if(r.ok)return r;}catch(error){void error;}await new Promise(resolve=>setTimeout(resolve,100));}throw new Error(`Preview did not become ready: ${url}`);}
try{await ready(`http://127.0.0.1:${apiPort}/api/health`);const page=await ready(base);const html=await page.text();assert.match(html,/manifest\.webmanifest/);const manifest=await(await fetch(`${base}/manifest.webmanifest`)).json();assert.equal(manifest.display,'standalone');assert.equal(manifest.name,'ZeroCloud Metro Simulator');assert.equal(manifest.icons[0].purpose,'any maskable');const worker=await(await fetch(`${base}/sw.js`)).text();assert.match(worker,/url\.pathname\.startsWith\('\/api\/'\)\)return/);const apiHealth=await(await fetch(`${base}/api/health`)).json();assert.equal(apiHealth.simulation,'synthetic');const state=await(await fetch(`${base}/api/state`)).json();assert.equal(state.scenario_id,'resort-20261114');console.log('PWA smoke passed: production shell, standalone manifest, service worker API bypass, same-origin local API proxy.');}finally{api.kill('SIGTERM');web.kill('SIGTERM');}
