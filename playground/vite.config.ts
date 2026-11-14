import { defineConfig } from 'vitest/config';
import react from '@vitejs/plugin-react';
const apiTarget=`http://127.0.0.1:${process.env.ZERO_CLOUD_API_PORT??4174}`;
export default defineConfig({plugins:[react()],base:'./',server:{proxy:{'/api':apiTarget}},preview:{proxy:{'/api':apiTarget}},test:{environment:'jsdom',setupFiles:['./tests/setup.ts'],include:['tests/**/*.test.{ts,tsx}']}});
