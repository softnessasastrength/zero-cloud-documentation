import { defineConfig } from 'vitest/config';
import react from '@vitejs/plugin-react';
export default defineConfig({plugins:[react()],base:'./',server:{proxy:{'/api':'http://127.0.0.1:4174'}},test:{environment:'jsdom',setupFiles:['./tests/setup.ts'],include:['tests/**/*.test.{ts,tsx}']}});
