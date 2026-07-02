import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import './index.css'
import App from './App.tsx'
import { AuthProvider } from "./AuthContext.tsx";
import { DateProvider } from "./DateContext.tsx";

createRoot(document.getElementById('root')).render(
  <StrictMode>
    <AuthProvider>
      <DateProvider>
        <App />
      </DateProvider>
    </AuthProvider>
  </StrictMode>,
)
