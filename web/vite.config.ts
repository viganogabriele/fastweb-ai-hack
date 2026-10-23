import react from '@vitejs/plugin-react'
import { defineConfig } from 'vite'
import { mockApi } from './mock-api/plugin.ts'

// The backend runs on :8000 (`make dev`); the UI only ever calls relative `/api/...` URLs.
// `npm run dev:mock` serves `/api` from `mock-api/` instead, for UI work without published runs.
const mock = process.env.VITE_API_MOCK === '1'

export default defineConfig({
  plugins: [react(), ...(mock ? [mockApi()] : [])],
  server: {
    host: '127.0.0.1',
    proxy: mock ? undefined : { '/api': process.env.TESSERA_API_TARGET ?? 'http://127.0.0.1:8000' },
  },
})
