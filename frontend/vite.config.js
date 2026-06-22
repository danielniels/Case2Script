import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// Dev only — proxy API calls to FastAPI backend on :8000
// In prod, FastAPI serves the built frontend directly (no proxy needed)
export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: {
      '/data': 'http://localhost:8000',
      '/runs': 'http://localhost:8000',
      '/suites': 'http://localhost:8000',
      '/convert': 'http://localhost:8000',
      '/mcp': 'http://localhost:8000',
      '/health': 'http://localhost:8000',
      '/submit-report': 'http://localhost:8000',
      '/api': 'http://localhost:8000',
    },
  },
})
