import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

export default defineConfig({
  plugins: [react()],
  server: {
    proxy: {
      '/query': {
        target: 'http://127.0.0.1:8111',
        changeOrigin: true,
      },
      '/health': {
        target: 'http://127.0.0.1:8111',
        changeOrigin: true,
      },
    },
  },
});
