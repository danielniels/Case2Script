import { useContext, useEffect, useRef, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { runs, screenshotUrl, scriptDownloadUrl, reportViewUrl } from '../api/client'
import { RunContext } from '../App'

function StepIcon({ status }) {
  if (status === 'passed') return (
    <svg className="w-4 h-4 text-green-400 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
      <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
    </svg>
  )
  if (status === 'failed') return (
    <svg className="w-4 h-4 text-red-400 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
      <path fillRule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clipRule="evenodd" />
    </svg>
  )
  if (status === 'running') return (
    <svg className="w-4 h-4 text-blue-400 animate-spin flex-shrink-0" fill="none" viewBox="0 0 24 24">
      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
    </svg>
  )
  return <span className="w-4 h-4 rounded-full border border-gray-700 flex-shrink-0 inline-block" />
}

function StepItem({ step, index }) {
  const { status, description } = step
  const rowBg =
    status === 'running' ? 'bg-blue-950/40' :
    status === 'failed'  ? 'bg-red-950/25'  : ''
  const textColor =
    status === 'pending' ? 'text-gray-600' :
    status === 'running' ? 'text-blue-200' :
    status === 'failed'  ? 'text-red-300'  : 'text-gray-300'
  const badge =
    status === 'running' ? <span className="text-xs text-blue-400 font-semibold">running</span> :
    status === 'passed'  ? <span className="text-xs text-green-400 font-semibold">PASS</span> :
    status === 'failed'  ? <span className="text-xs text-red-400 font-semibold">FAIL</span> : null

  return (
    <div className={`flex items-center gap-2.5 px-3 py-2 rounded-md ${rowBg}`}>
      <StepIcon status={status} />
      <span className="text-xs text-gray-600 font-mono w-5 flex-shrink-0 text-right">{index + 1}</span>
      <span className={`text-sm flex-1 min-w-0 truncate ${textColor}`}>{description}</span>
      {badge}
    </div>
  )
}

const PLACEHOLDER = `{
  "suite_id": "suite-001",
  "test_case_id": "TC-001",
  "test_case_name": "Login Test",
  "test_data": { "username": "admin@mail.com", "password": "secret" },
  "steps": [
    { "test_step_id": "1", "test_step_description": "Navigate to https://app.example.com/login" },
    { "test_step_id": "2", "test_step_description": "Mengisi Username \\u2192 admin@mail.com" },
    { "test_step_id": "3", "test_step_description": "Mengisi Password \\u2192 secret" },
    { "test_step_id": "4", "test_step_description": "Click Login button" },
    { "test_step_id": "5", "test_step_description": "Halaman Dashboard" }
  ]
}`

export default function RunPage() {
  const navigate = useNavigate()
  const { setLastRunId } = useContext(RunContext)
  const [jsonInput, setJsonInput] = useState('')
  const [isStarting, setIsStarting] = useState(false)
  const [parseError, setParseError] = useState(null)

  const [runId, setRunId] = useState(null)
  const [runStatus, setRunStatus] = useState(null)
  const [allSteps, setAllSteps] = useState([])
  const [latestScreenshot, setLatestScreenshot] = useState(null)

  const esRef = useRef(null)
  const pollRef = useRef(null)
  const stepMapRef = useRef({})
  const allStepsRef = useRef([])

  const isRunning = runStatus?.status === 'running'

  // Keep allStepsRef in sync so SSE handler can use the latest value
  useEffect(() => { allStepsRef.current = allSteps }, [allSteps])

  // SSE subscription for step-level events
  useEffect(() => {
    if (!runId) return
    stepMapRef.current = {}

    const es = runs.events(runId)
    esRef.current = es

    es.onmessage = (e) => {
      let ev
      try { ev = JSON.parse(e.data) } catch { return }

      if (ev.type === 'step_start') {
        stepMapRef.current[ev.step_index] = {
          status: 'running',
          description: ev.step_description,
          screenshot_path: null,
          error: null,
        }
        setAllSteps(prev => {
          const next = [...prev]
          const idx = ev.step_index - 1
          if (next[idx]) next[idx] = { ...next[idx], status: 'running' }
          return next
        })
      } else if (ev.type === 'step_end') {
        const entry = {
          status: ev.ok ? 'passed' : 'failed',
          description: ev.step_description,
          screenshot_path: ev.screenshot_path || null,
          error: ev.error || null,
        }
        stepMapRef.current[ev.step_index] = entry
        setAllSteps(prev => {
          const next = [...prev]
          const idx = ev.step_index - 1
          if (next[idx]) next[idx] = { ...next[idx], ...entry }
          return next
        })
        if (ev.screenshot_path) setLatestScreenshot(ev.screenshot_path)
      } else if (ev.type === 'run_end' || ev.type === 'done') {
        setRunStatus(prev => ({ ...(prev || {}), status: ev.status || 'passed' }))
        es.close()
      } else if (ev.type === 'critical_failure') {
        setRunStatus(prev => ({ ...(prev || {}), status: 'failed' }))
      }
    }
    es.onerror = () => es.close()

    return () => { es.close(); esRef.current = null }
  }, [runId])

  // Polling for overall run status (current_step, script_path, report_path)
  useEffect(() => {
    if (!runId) return

    const poll = async () => {
      try {
        const data = await runs.get(runId)
        setRunStatus(data)
        if (data.status !== 'running') {
          clearInterval(pollRef.current)
        }
      } catch {
        clearInterval(pollRef.current)
      }
    }

    poll()
    pollRef.current = setInterval(poll, 2000)
    return () => clearInterval(pollRef.current)
  }, [runId])

  const handleStart = async () => {
    setParseError(null)
    let parsed
    try {
      parsed = JSON.parse(jsonInput.trim())
    } catch (e) {
      setParseError('Invalid JSON: ' + e.message)
      return
    }

    if (!parsed.suite_id || !parsed.test_case_id || !Array.isArray(parsed.steps)) {
      setParseError('Required fields: suite_id, test_case_id, steps[]')
      return
    }

    setIsStarting(true)
    setLatestScreenshot(null)
    stepMapRef.current = {}

    const initialSteps = parsed.steps.map(s => ({
      status: 'pending',
      description: s.test_step_description || s.description || s.step || `Step`,
      screenshot_path: null,
      error: null,
    }))
    setAllSteps(initialSteps)

    try {
      const result = await runs.start({
        suite_id: parsed.suite_id,
        test_case_id: parsed.test_case_id,
        test_case_name: parsed.test_case_name || '',
        test_data: parsed.test_data || {},
        steps: parsed.steps,
        session_id: parsed.session_id || undefined,
      })
      setRunId(result.run_id)
      setRunStatus({ status: 'running', ...result })
      setLastRunId(result.run_id)  // update sidebar link via context (no localStorage = no stale runId)
    } catch (e) {
      setParseError('Failed to start run: ' + e.message)
      setAllSteps([])
    } finally {
      setIsStarting(false)
    }
  }

  const handleStop = async () => {
    if (!runId) return
    try {
      await runs.stop(runId)
      setRunStatus(prev => ({ ...(prev || {}), status: 'stopped' }))
    } catch (e) {
      console.error('Stop failed:', e)
    }
  }

  const completedCount = allSteps.filter(s => s.status === 'passed' || s.status === 'failed').length
  const totalCount = allSteps.length
  const progress = totalCount > 0 ? (completedCount / totalCount) * 100 : 0

  const statusBadge =
    !runStatus ? null :
    runStatus.status === 'running' ? 'bg-blue-600 text-white' :
    runStatus.status === 'passed'  ? 'bg-green-700 text-white' :
    runStatus.status === 'failed'  ? 'bg-red-700 text-white'  :
    'bg-gray-600 text-white'

  return (
    <div className="p-6 space-y-4">
      {/* Header */}
      <div className="flex items-center justify-between">
        <h1 className="text-xl font-semibold text-white">Run Test</h1>
        {runStatus && (
          <div className="flex items-center gap-3">
            <span className="text-xs text-gray-500 font-mono">{runId}</span>
            <span className={`text-xs font-bold px-2.5 py-1 rounded-full ${statusBadge}`}>
              {runStatus.status?.toUpperCase()}
            </span>
            <button
              onClick={() => navigate(`/runs/${runId}`)}
              className="text-xs text-indigo-400 hover:text-indigo-300 underline"
            >
              View Detail →
            </button>
          </div>
        )}
      </div>

      {/* Blok 1 — JSON Input */}
      <div className="bg-gray-900 rounded-xl border border-gray-800 p-4 space-y-3">
        <h2 className="text-sm font-semibold text-gray-300 flex items-center gap-2">
          <span className="w-5 h-5 rounded-full bg-indigo-600 flex items-center justify-center text-xs text-white font-bold flex-shrink-0">1</span>
          Test Case JSON
        </h2>
        <textarea
          className="w-full h-40 bg-gray-950 border border-gray-700 rounded-lg p-3 text-sm font-mono text-green-400 resize-y focus:outline-none focus:border-indigo-500 transition-colors"
          placeholder={PLACEHOLDER}
          value={jsonInput}
          onChange={e => setJsonInput(e.target.value)}
          disabled={isRunning}
          spellCheck={false}
        />
        {parseError && <p className="text-red-400 text-xs">{parseError}</p>}
        <div className="flex gap-2">
          <button
            onClick={handleStart}
            disabled={isStarting || isRunning || !jsonInput.trim()}
            className="px-4 py-2 bg-indigo-600 hover:bg-indigo-500 disabled:opacity-40 disabled:cursor-not-allowed text-white text-sm font-medium rounded-lg transition-colors"
          >
            {isStarting ? 'Starting…' : isRunning ? 'Running…' : 'Run Test'}
          </button>
          {isRunning && (
            <button
              onClick={handleStop}
              className="px-4 py-2 bg-red-700 hover:bg-red-600 text-white text-sm font-medium rounded-lg transition-colors"
            >
              Stop
            </button>
          )}
        </div>
      </div>

      {/* Blok 2 + 3 row */}
      <div className="grid grid-cols-5 gap-4">

        {/* Blok 2 — Live Steps */}
        <div className="col-span-3 bg-gray-900 rounded-xl border border-gray-800 p-4 space-y-3">
          <div className="flex items-center justify-between">
            <h2 className="text-sm font-semibold text-gray-300 flex items-center gap-2">
              <span className="w-5 h-5 rounded-full bg-indigo-600 flex items-center justify-center text-xs text-white font-bold flex-shrink-0">2</span>
              Live Steps
            </h2>
            {totalCount > 0 && (
              <span className="text-xs text-gray-500">{completedCount} / {totalCount}</span>
            )}
          </div>

          {totalCount > 0 && (
            <div className="bg-gray-800 rounded-full h-1.5 overflow-hidden">
              <div
                className="bg-indigo-500 h-1.5 transition-all duration-500"
                style={{ width: `${progress}%` }}
              />
            </div>
          )}

          <div className="space-y-0.5 max-h-80 overflow-y-auto">
            {allSteps.length === 0 ? (
              <p className="text-gray-600 text-sm text-center py-10">
                Paste a test case JSON and click Run Test
              </p>
            ) : (
              allSteps.map((step, i) => (
                <StepItem key={i} step={step} index={i} />
              ))
            )}
          </div>
        </div>

        {/* Blok 3 — Screenshot + Downloads */}
        <div className="col-span-2 bg-gray-900 rounded-xl border border-gray-800 p-4 space-y-3 flex flex-col">
          <h2 className="text-sm font-semibold text-gray-300 flex items-center gap-2">
            <span className="w-5 h-5 rounded-full bg-indigo-600 flex items-center justify-center text-xs text-white font-bold flex-shrink-0">3</span>
            Results
          </h2>

          {/* Screenshot preview */}
          <div className="bg-gray-950 rounded-lg overflow-hidden border border-gray-800 flex items-center justify-center" style={{ aspectRatio: '16/9' }}>
            {latestScreenshot ? (
              <img
                src={screenshotUrl(latestScreenshot)}
                alt="Latest step screenshot"
                className="w-full h-full object-contain"
                onError={ev => { ev.target.style.display = 'none' }}
              />
            ) : (
              <p className="text-gray-700 text-xs">No screenshot yet</p>
            )}
          </div>

          {/* Download buttons */}
          <div className="space-y-2 flex-1">
            {runStatus?.script_path ? (
              <a
                href={scriptDownloadUrl(runStatus.script_path)}
                download
                className="flex items-center gap-2.5 w-full px-3 py-2.5 bg-gray-800 hover:bg-gray-700 rounded-lg text-xs text-gray-300 transition-colors"
              >
                <svg className="w-4 h-4 text-yellow-400 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
                </svg>
                Download Playwright Script (.js)
              </a>
            ) : (
              <div className="flex items-center gap-2.5 w-full px-3 py-2.5 bg-gray-800/50 rounded-lg text-xs text-gray-700">
                <svg className="w-4 h-4 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
                </svg>
                Download Playwright Script (.js)
              </div>
            )}

            {runStatus?.report_path ? (
              <a
                href={reportViewUrl(runStatus.report_path)}
                download
                className="flex items-center gap-2.5 w-full px-3 py-2.5 bg-gray-800 hover:bg-gray-700 rounded-lg text-xs text-gray-300 transition-colors"
              >
                <svg className="w-4 h-4 text-green-400 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                </svg>
                Download Test Report (.json)
              </a>
            ) : (
              <div className="flex items-center gap-2.5 w-full px-3 py-2.5 bg-gray-800/50 rounded-lg text-xs text-gray-700">
                <svg className="w-4 h-4 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                </svg>
                Download Test Report (.json)
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}
