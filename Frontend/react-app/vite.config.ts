import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import { nodePolyfills } from 'vite-plugin-node-polyfills'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [
    react(),
    nodePolyfills({
      // Para soportar node-forge en el navegador
      globals: {
        Buffer: true,
        global: true,
        process: true,
      },
    }),
  ],
  base: '/admin/',  // Base URL para los assets en producción
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
        target: 'http://localhost:8000/admin',
        changeOrigin: true,
        secure: false,
      },
      '/static': {
        target: 'http://localhost:8000/admin',
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
