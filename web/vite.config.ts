import react from '@vitejs/plugin-react'
import { defineConfig } from 'vite'

// The backend runs on :8000 (`make dev`); the UI only ever calls relative `/api/...` URLs.
export default defineConfig({
  plugins: [react()],
  server: {
    host: '127.0.0.1',
    proxy: { '/api': 'http://127.0.0.1:8000' },
  },
})
