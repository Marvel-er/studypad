import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    proxy: {
      '/api': 'http://localhost:8799',
    },
  },
  build: {
    // The complete 3,600-word dataset is an intentional lazy-loaded data chunk.
    chunkSizeWarningLimit: 600,
  },
})
