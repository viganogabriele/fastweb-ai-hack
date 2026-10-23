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
    // DEMO-04: the phone reaches /store/record through an HTTPS tunnel (the microphone needs a
    // secure context), e.g. `cloudflared tunnel --url http://127.0.0.1:5173`.
    allowedHosts: ['.trycloudflare.com', '.ngrok-free.app'],
    proxy: mock ? undefined : { '/api': 'http://127.0.0.1:8000' },
  },
})
