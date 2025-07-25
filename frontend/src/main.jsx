import React from 'react'
import ReactDOM from 'react-dom/client'
import App from './App.jsx'
import './index.css'
import { Toaster } from 'react-hot-toast'

ReactDOM.createRoot(document.getElementById('root')).render(
    <React.StrictMode>
        <App />
        <Toaster position="top-right" toastOptions={{
            style: {
                background: '#1e293b',
                color: '#f8fafc',
                border: '1px solid rgba(148, 163, 184, 0.2)'
            },
        }} />
    </React.StrictMode>,
)