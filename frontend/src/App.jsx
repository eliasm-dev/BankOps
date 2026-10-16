/**
 * BankOps — Root Application Component
 *
 * Sets up routing and global providers.
 * Placeholder until Stage 4 wires in the full navigation.
 */
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'

function App() {
  return (
    <BrowserRouter>
      <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
        <div className="flex items-center justify-center min-h-screen">
          <div className="card p-8 max-w-md text-center">
            <h1 className="text-3xl font-bold text-navy-800 dark:text-white mb-2">
              BankOps
            </h1>
            <p className="text-gray-500 dark:text-gray-400 mb-4">
              Banking Operations &amp; Database Monitoring System
            </p>
            <p className="text-sm text-gray-400 dark:text-gray-500">
              Stage 1 complete — frontend scaffold ready.
              <br />
              Authentication, routing, and dashboard come in Stages 3–4.
            </p>
          </div>
        </div>
      </div>
    </BrowserRouter>
  )
}

export default App
