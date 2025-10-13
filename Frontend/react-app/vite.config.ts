import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    port: 3000,
    host: true, // Escuchar en todas las interfaces de red
    strictPort: false,
    hmr: {
      clientPort: 3000,
    },
    allowedHosts: [
      '.trycloudflare.com', // Permitir todos los subdominios de Cloudflare
      'localhost',
    ],
    proxy: {
      '/api': {
        target: 'http://localhost:8002',
        changeOrigin: true,
        secure: false,
      },
      '/static': {
        target: 'http://localhost:8002',
        changeOrigin: true,
        secure: false,
      }
    }
  },
  build: {
    outDir: 'dist',
    sourcemap: true,
  }
})
