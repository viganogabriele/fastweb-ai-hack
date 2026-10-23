import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import './index.css'
import App from './App.tsx'
import { RecordPage } from './store/RecordPage.tsx'

// The store's phone page lives on its own path (opened from a QR), outside the dashboard shell.
const isRecordPage = window.location.pathname.replace(/\/+$/, '') === '/store/record'

createRoot(document.getElementById('root')!).render(
  <StrictMode>{isRecordPage ? <RecordPage /> : <App />}</StrictMode>,
)
