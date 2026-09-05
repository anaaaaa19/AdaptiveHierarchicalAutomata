import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    port: 3000,
    proxy: {
      '/status': 'http://127.0.0.1:8000',
      '/health': 'http://127.0.0.1:8000',
      '/events': 'http://127.0.0.1:8000',
      '/alerts': 'http://127.0.0.1:8000',
      '/models': 'http://127.0.0.1:8000',
      '/sessions': 'http://127.0.0.1:8000',
      '/metrics': 'http://127.0.0.1:8000',
      '/drift': 'http://127.0.0.1:8000',
      '/adaptation': 'http://127.0.0.1:8000',
      '/investigations': 'http://127.0.0.1:8000',
      '/experiments': 'http://127.0.0.1:8000',
      '/capture': 'http://127.0.0.1:8000',
    },
  },
  test: {
    globals: true,
    environment: 'jsdom',
  },
});
