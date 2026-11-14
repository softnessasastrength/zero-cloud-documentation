import { defineConfig } from 'vitest/config';
import react from '@vitejs/plugin-react';
const transitProxy={target:`http://127.0.0.1:${process.env.PERCIVAL_TRANSIT_PORT??8765}`,rewrite:(path:string)=>path.replace(/^\/transit-api/,'')};
const apiTarget=`http://127.0.0.1:${process.env.ZERO_CLOUD_API_PORT??4174}`;
export default defineConfig({plugins:[react()],base:'./',server:{proxy:{'/api':apiTarget,'/transit-api':transitProxy}},preview:{proxy:{'/api':apiTarget,'/transit-api':transitProxy}},test:{environment:'jsdom',setupFiles:['./tests/setup.ts'],include:['tests/**/*.test.{ts,tsx}']}});
