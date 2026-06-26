import { createContext, useContext, useState } from 'react'
import { BrowserRouter, Routes, Route, NavLink } from 'react-router-dom'
import RunPage from './pages/RunPage'
import RunDetailPage from './pages/RunDetailPage'
import ScriptEditor from './pages/ScriptEditor'

// Shared context so RunPage can tell Sidebar which run just started —
// no localStorage, so there's never a stale run_id from a dead server session.
export const RunContext = createContext({ lastRunId: null, setLastRunId: () => {} })

function Sidebar() {
  const { lastRunId } = useContext(RunContext)

  const linkCls = ({ isActive }) =>
    `flex items-center gap-2.5 px-3 py-2 rounded-lg text-sm font-medium transition-colors ${
      isActive
        ? 'bg-indigo-600 text-white'
        : 'text-gray-400 hover:bg-gray-800 hover:text-gray-200'
    }`

  return (
    <aside id="sidebar" className="w-52 bg-gray-900 min-h-screen flex flex-col border-r border-gray-800 flex-shrink-0">
      <div className="px-4 py-5">
        <div className="flex items-center gap-2.5">
          <div className="w-8 h-8 rounded-lg bg-indigo-600 flex items-center justify-center flex-shrink-0">
            <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" class="size-6">
              <path fill-rule="evenodd" d="M2.25 6a3 3 0 0 1 3-3h13.5a3 3 0 0 1 3 3v12a3 3 0 0 1-3 3H5.25a3 3 0 0 1-3-3V6Zm3.97.97a.75.75 0 0 1 1.06 0l2.25 2.25a.75.75 0 0 1 0 1.06l-2.25 2.25a.75.75 0 0 1-1.06-1.06l1.72-1.72-1.72-1.72a.75.75 0 0 1 0-1.06Zm4.28 4.28a.75.75 0 0 0 0 1.5h3a.75.75 0 0 0 0-1.5h-3Z" clip-rule="evenodd" />
            </svg>
          </div>
          <div>
            <p className="text-white font-bold text-sm leading-tight">Case2Script</p>
            <p className="text-gray-500 text-xs">Test Automation</p>
          </div>
        </div>
      </div>

      <nav id="sidebar-nav" className="flex-1 px-3 py-2 space-y-1">
        <NavLink id="nav-run-test" to="/" className={linkCls} end>
          <svg className="w-4 h-4 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M14.752 11.168l-3.197-2.132A1 1 0 0010 9.87v4.263a1 1 0 001.555.832l3.197-2.132a1 1 0 000-1.664z" />
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          Run Test
        </NavLink>

        {lastRunId ? (
          <NavLink id="nav-run-detail" to={`/runs/${lastRunId}`} className={linkCls}>
            <svg className="w-4 h-4 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-3 7h3m-3 4h3m-6-4h.01M9 16h.01" />
            </svg>
            Run Detail
          </NavLink>
        ) : (
          <span className="flex items-center gap-2.5 px-3 py-2 rounded-lg text-sm font-medium text-gray-700 cursor-not-allowed select-none">
            <svg className="w-4 h-4 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-3 7h3m-3 4h3m-6-4h.01M9 16h.01" />
            </svg>
            Run Detail
          </span>
        )}
      </nav>

      <div className="px-4 py-3 border-t border-gray-800">
        <p className="text-xs text-gray-700">Powered by Playwright</p>
      </div>
    </aside>
  )
}

function Layout() {
  const [lastRunId, setLastRunId] = useState(null)

  return (
    <RunContext.Provider value={{ lastRunId, setLastRunId }}>
      <div className="min-h-screen bg-gray-950 text-gray-100 flex">
        <Sidebar />
        <main id="main-content" className="flex-1 overflow-auto min-h-screen">
          <Routes>
            <Route path="/" element={<RunPage />} />
            <Route path="/runs/:runId" element={<RunDetailPage />} />
            <Route path="/scripts/:scriptPath" element={<ScriptEditor />} />
          </Routes>
        </main>
      </div>
    </RunContext.Provider>
  )
}

export default function App() {
  return (
    <BrowserRouter>
      <Layout />
    </BrowserRouter>
  )
}
