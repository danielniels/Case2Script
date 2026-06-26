import { useContext, useEffect, useRef, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { runs, converters, screenshotUrl, scriptDownloadUrl, reportViewUrl } from '../api/client'
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
  if (status === 'stopped') return (
    <span className="w-4 h-4 rounded-full bg-gray-600 flex-shrink-0 inline-block" />
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
    status === 'failed'  ? <span className="text-xs text-red-400 font-semibold">FAIL</span> :
    status === 'stopped' ? <span className="text-xs text-gray-500 font-semibold">STOPPED</span> : null

  return (
    <div className={`flex items-center gap-2.5 px-3 py-2 rounded-md ${rowBg}`}>
      <StepIcon status={status} />
      <span className="text-xs text-gray-600 font-mono w-5 flex-shrink-0 text-right">{index + 1}</span>
      <span className={`text-sm flex-1 min-w-0 truncate ${textColor}`}>{description}</span>
      {badge}
    </div>
  )
}

const JSON_PLACEHOLDER = `{
  "suite_id": "suite-001",
  "test_case_id": "TC-001",
  "test_case_name": "Login Test",
  "test_data": { "username": "admin@mail.com", "password": "secret" },
  "steps": [
    { "test_step_id": "1", "test_step_description": "Navigate to https://app.example.com/login" },
    { "test_step_id": "2", "test_step_description": "Fill username field with admin@mail.com" },
    { "test_step_id": "3", "test_step_description": "Fill password field with secret" },
    { "test_step_id": "4", "test_step_description": "Click Login button" },
    { "test_step_id": "5", "test_step_description": "Verify dashboard page is visible" }
  ]
}`

const PROMPT_PLACEHOLDER =
`1. Open https://example.com/login
2. Type 'admin@mail.com' in the username input
3. Type 'secret' in the password input
4. Click the Login button
5. Verify the dashboard is shown`

const TABS = [
  { id: 'json',   label: 'JSON' },
  { id: 'excel',  label: 'Excel' },
  { id: 'prompt', label: 'Prompt' },
]

export default function RunPage() {
  const navigate = useNavigate()
  const { setLastRunId } = useContext(RunContext)

  // ── Input mode ─────────────────────────────────────────────────────────────
  const [inputMode, setInputMode]     = useState('json')

  // JSON
  const [jsonInput, setJsonInput]     = useState('')

  // Excel
  const [excelFile, setExcelFile]     = useState(null)

  // Prompt
  const [promptText, setPromptText]   = useState('')
  const [promptName, setPromptName]   = useState('')

  // Shared convert state (Excel + Prompt)
  const [converting, setConverting]   = useState(false)
  const [convertError, setConvertError] = useState(null)
  const [suite, setSuite]             = useState(null)
  const [selectedTcIdx, setSelectedTcIdx] = useState(0)

  // ── Run state ──────────────────────────────────────────────────────────────
  const [isStarting, setIsStarting]   = useState(false)
  const [parseError, setParseError]   = useState(null)
  const [runId, setRunId]             = useState(null)
  const [runStatus, setRunStatus]     = useState(null)
  const [allSteps, setAllSteps]       = useState([])
  const [latestScreenshot, setLatestScreenshot] = useState(null)
  const [startTime, setStartTime]     = useState(null)
  const [elapsed, setElapsed]         = useState(0)
  const [finalDuration, setFinalDuration] = useState(null)

  const esRef       = useRef(null)
  const pollRef     = useRef(null)
  const timerRef    = useRef(null)
  const stepMapRef  = useRef({})
  const allStepsRef = useRef([])

  const isRunning = runStatus?.status === 'running'

  useEffect(() => { allStepsRef.current = allSteps }, [allSteps])

  // Elapsed timer
  useEffect(() => {
    if (isRunning && startTime) {
      timerRef.current = setInterval(() => {
        setElapsed(Math.floor((Date.now() - startTime) / 1000))
      }, 1000)
    } else {
      clearInterval(timerRef.current)
      if (startTime && !isRunning && runStatus) setFinalDuration(elapsed)
    }
    return () => clearInterval(timerRef.current)
  }, [isRunning, startTime])

  // SSE subscription
  useEffect(() => {
    if (!runId) return
    stepMapRef.current = {}

    const es = runs.events(runId)
    esRef.current = es

    es.onmessage = (e) => {
      let ev
      try { ev = JSON.parse(e.data) } catch { return }

      if (ev.type === 'step_start') {
        stepMapRef.current[ev.step_index] = { status: 'running', description: ev.step_description, screenshot_path: null, error: null }
        setAllSteps(prev => {
          const next = [...prev]
          const idx = ev.step_index - 1
          if (next[idx]) next[idx] = { ...next[idx], status: 'running' }
          return next
        })
      } else if (ev.type === 'step_end') {
        const entry = { status: ev.ok ? 'passed' : 'failed', description: ev.step_description, screenshot_path: ev.screenshot_path || null, error: ev.error || null }
        stepMapRef.current[ev.step_index] = entry
        setAllSteps(prev => {
          const next = [...prev]
          const idx = ev.step_index - 1
          if (next[idx]) next[idx] = { ...next[idx], ...entry }
          return next
        })
        if (ev.screenshot_path) setLatestScreenshot(ev.screenshot_path)
      } else if (ev.type === 'stopped') {
        setRunStatus(prev => ({ ...(prev || {}), status: 'stopped' }))
        es.close()
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

  // Polling for script_path / report_path
  useEffect(() => {
    if (!runId) return
    const poll = async () => {
      try {
        const data = await runs.get(runId)
        setRunStatus(prev => {
          // Never let a stale poll overwrite a terminal status
          if (prev?.status && prev.status !== 'running') return prev
          return data
        })
        if (data.status !== 'running') clearInterval(pollRef.current)
      } catch {
        clearInterval(pollRef.current)
      }
    }
    poll()
    pollRef.current = setInterval(poll, 2000)
    return () => clearInterval(pollRef.current)
  }, [runId])

  // ── Handlers ───────────────────────────────────────────────────────────────

  function switchMode(mode) {
    if (isRunning) return
    setInputMode(mode)
    setSuite(null)
    setConvertError(null)
    setParseError(null)
  }

  async function handleConvert() {
    setConvertError(null)
    setSuite(null)
    setConverting(true)
    try {
      const result = inputMode === 'excel'
        ? await converters.fromExcel(excelFile)
        : await converters.fromPrompt(promptText.trim(), promptName.trim())
      setSuite(result)
      setSelectedTcIdx(0)
    } catch (err) {
      setConvertError(err.message || 'Conversion failed')
    } finally {
      setConverting(false)
    }
  }

  const handleStart = async () => {
    setParseError(null)
    let payload

    if (inputMode === 'json') {
      let parsed
      try { parsed = JSON.parse(jsonInput.trim()) } catch (e) {
        setParseError('Invalid JSON: ' + e.message); return
      }
      if (!parsed.suite_id || !parsed.test_case_id || !Array.isArray(parsed.steps)) {
        setParseError('Required fields: suite_id, test_case_id, steps[]'); return
      }
      payload = {
        suite_id: parsed.suite_id,
        test_case_id: parsed.test_case_id,
        test_case_name: parsed.test_case_name || '',
        test_data: parsed.test_data || {},
        steps: parsed.steps,
        session_id: parsed.session_id || undefined,
      }
    } else {
      if (!suite) { setParseError('Convert the input first'); return }
      const tc = suite.test_cases?.[selectedTcIdx]
      if (!tc?.steps?.length) { setParseError('No steps found in selected test case'); return }
      payload = {
        suite_id: suite.id,
        test_case_id: tc.test_case_id,
        test_case_name: tc.test_case_name || '',
        test_data: tc.test_data || {},
        steps: tc.steps,
      }
    }

    setIsStarting(true)
    setLatestScreenshot(null)
    setStartTime(Date.now())
    setElapsed(0)
    setFinalDuration(null)
    stepMapRef.current = {}

    setAllSteps(payload.steps.map(s => ({
      status: 'pending',
      description: s.test_step_description || s.description || s.step || 'Step',
      screenshot_path: null,
      error: null,
    })))

    try {
      const result = await runs.start(payload)
      setRunId(result.run_id)
      setRunStatus({ status: 'running', ...result })
      setLastRunId(result.run_id)
    } catch (e) {
      setParseError('Failed to start run: ' + e.message)
      setAllSteps([])
    } finally {
      setIsStarting(false)
    }
  }

  const handleStop = async () => {
    if (!runId) return
    // Optimistic update: freeze UI immediately — don't wait for HTTP response
    setRunStatus(prev => ({ ...(prev || {}), status: 'stopped' }))
    setAllSteps(prev => prev.map(s => s.status === 'running' ? { ...s, status: 'stopped' } : s))
    clearInterval(pollRef.current)
    if (esRef.current) { esRef.current.close(); esRef.current = null }
    try {
      await runs.stop(runId)
    } catch (e) {
      console.error('Stop failed:', e)
    }
  }

  const fmtDuration = (secs) => {
    const m = Math.floor(secs / 60), s = secs % 60
    return m > 0 ? `${m}m ${s}s` : `${s}s`
  }

  const completedCount = allSteps.filter(s => s.status === 'passed' || s.status === 'failed').length
  const totalCount     = allSteps.length
  const progress       = totalCount > 0 ? (completedCount / totalCount) * 100 : 0

  const statusBadge =
    !runStatus ? null :
    runStatus.status === 'running' ? 'bg-blue-600 text-white' :
    runStatus.status === 'passed'  ? 'bg-green-700 text-white' :
    runStatus.status === 'failed'  ? 'bg-red-700 text-white'  :
    'bg-gray-600 text-white'

  const canConvert = inputMode === 'excel' ? !!excelFile : promptText.trim().length > 0
  const canRun     = !isStarting && !isRunning && !converting && (
    inputMode === 'json' ? jsonInput.trim().length > 0 : !!suite
  )

  const selectedTc = suite?.test_cases?.[selectedTcIdx]
  const errorMsg   = parseError || convertError

  return (
    <div id="run-page" className="p-6 space-y-4">

      {/* Header */}
      <div id="run-header" className="flex items-center justify-between">
        <h1 className="text-xl font-semibold text-white">Run Test</h1>
        {runStatus && (
          <div className="flex items-center gap-3">
            <span id="run-id-display" className="text-xs text-gray-500 font-mono">{runId}</span>
            <span id="run-status-badge" className={`text-xs font-bold px-2.5 py-1 rounded-full ${statusBadge}`}>
              {runStatus.status?.toUpperCase()}
            </span>
            {startTime && (
              <span id="run-timer" className="text-xs text-gray-500 font-mono">
                {new Date(startTime).toLocaleTimeString()}
                {' · '}
                {isRunning
                  ? <span className="text-blue-400">{fmtDuration(elapsed)}</span>
                  : <span className="text-gray-400">{fmtDuration(finalDuration ?? elapsed)}</span>
                }
              </span>
            )}
            <button
              id="view-detail-btn"
              onClick={() => navigate(`/runs/${runId}`)}
              className="text-xs text-indigo-400 hover:text-indigo-300 underline"
            >
              View Detail →
            </button>
          </div>
        )}
      </div>

      {/* ── Blok 1 — Input ─────────────────────────────────────────────────── */}
      <div id="input-panel" className="bg-gray-900 rounded-xl border border-gray-800 p-4 space-y-3">
        <h2 className="text-sm font-semibold text-gray-300 flex items-center gap-2">
          <span className="w-5 h-5 rounded-full bg-indigo-600 flex items-center justify-center text-xs text-white font-bold flex-shrink-0">1</span>
          Test Input
        </h2>

        {/* Tab bar */}
        <div className="flex gap-0 border-b border-gray-800 -mx-4 px-4">
          {TABS.map(({ id, label }) => (
            <button
              key={id}
              id={`tab-${id}`}
              onClick={() => switchMode(id)}
              disabled={isRunning}
              className={`px-4 py-2 text-xs font-semibold tracking-wide border-b-2 -mb-px transition-colors ${
                inputMode === id
                  ? 'text-indigo-400 border-indigo-500'
                  : 'text-gray-500 hover:text-gray-300 border-transparent disabled:cursor-not-allowed'
              }`}
            >
              {label}
            </button>
          ))}
        </div>

        {/* JSON panel */}
        {inputMode === 'json' && (
          <textarea
            id="json-textarea"
            className="w-full h-40 bg-gray-950 border border-gray-700 rounded-lg p-3 text-sm font-mono text-green-400 resize-y focus:outline-none focus:border-indigo-500 transition-colors"
            placeholder={JSON_PLACEHOLDER}
            value={jsonInput}
            onChange={e => setJsonInput(e.target.value)}
            disabled={isRunning}
            spellCheck={false}
          />
        )}

        {/* Excel panel */}
        {inputMode === 'excel' && (
          <div className="space-y-2.5">
            <label className="flex items-center gap-2.5 px-3 py-3 bg-gray-800 hover:bg-gray-700 border border-dashed border-gray-600 hover:border-gray-500 rounded-lg cursor-pointer transition-colors w-full">
              <svg className="w-4 h-4 text-green-400 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
              </svg>
              <span className="text-xs text-gray-300 flex-1 min-w-0 truncate">
                {excelFile ? excelFile.name : 'Click to choose .xlsx file'}
              </span>
              {excelFile && (
                <span className="text-xs text-gray-500">{(excelFile.size / 1024).toFixed(1)} KB</span>
              )}
              <input
                type="file"
                accept=".xlsx,.xls"
                className="hidden"
                onChange={e => { setExcelFile(e.target.files[0] || null); setSuite(null); setConvertError(null) }}
              />
            </label>
            <a
              href={converters.excelTemplate()}
              download="test_suite_template.xlsx"
              className="inline-flex items-center gap-1.5 text-xs text-indigo-400 hover:text-indigo-300 transition-colors"
            >
              <svg className="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
              </svg>
              Download template
            </a>
            <p className="text-xs text-gray-600">
              Required column: <span className="font-mono text-gray-500">test_step_description</span>.
              Optional: <span className="font-mono text-gray-500">test_suite_id, test_case_id, test_case_name, test_step_id, expected_result</span>
            </p>
          </div>
        )}

        {/* Prompt panel */}
        {inputMode === 'prompt' && (
          <div className="space-y-2">
            <input
              type="text"
              placeholder="Test case name (optional)"
              value={promptName}
              onChange={e => setPromptName(e.target.value)}
              disabled={isRunning}
              className="w-full bg-gray-950 border border-gray-700 rounded-lg px-3 py-2 text-xs text-gray-300 placeholder-gray-600 focus:outline-none focus:border-indigo-500 transition-colors"
            />
            <textarea
              className="w-full h-36 bg-gray-950 border border-gray-700 rounded-lg p-3 text-sm font-mono text-green-400 resize-y focus:outline-none focus:border-indigo-500 transition-colors"
              placeholder={PROMPT_PLACEHOLDER}
              value={promptText}
              onChange={e => { setPromptText(e.target.value); setSuite(null) }}
              disabled={isRunning}
              spellCheck={false}
            />
            <p className="text-xs text-gray-600">
              Numbered list (1. 2. 3.) → parsed instantly without LLM.
              Natural language → sent to Ollama to structure.
            </p>
          </div>
        )}

        {/* Error */}
        {errorMsg && (
          <p id="input-error" className="text-red-400 text-xs">{errorMsg}</p>
        )}

        {/* Suite preview (after convert) */}
        {suite && inputMode !== 'json' && (
          <div id="suite-preview" className="bg-gray-950 border border-gray-700 rounded-lg p-3 space-y-2">
            <div className="flex items-center justify-between gap-2">
              <p className="text-xs text-gray-300 font-semibold truncate">{suite.name}</p>
              {suite.test_cases.length > 1 && (
                <span className="text-xs text-gray-600 flex-shrink-0">{suite.test_cases.length} test cases</span>
              )}
            </div>

            {suite.test_cases.length > 1 && (
              <select
                value={selectedTcIdx}
                onChange={e => setSelectedTcIdx(Number(e.target.value))}
                className="w-full bg-gray-900 border border-gray-700 rounded px-2 py-1.5 text-xs text-gray-300 focus:outline-none focus:border-indigo-500"
              >
                {suite.test_cases.map((tc, i) => (
                  <option key={i} value={i}>{tc.test_case_id} — {tc.test_case_name}</option>
                ))}
              </select>
            )}

            <div className="max-h-28 overflow-y-auto space-y-0.5">
              {selectedTc?.steps.map((step, i) => (
                <div key={i} className="flex gap-2 text-xs">
                  <span className="text-gray-600 font-mono flex-shrink-0 w-5 text-right">{i + 1}.</span>
                  <span className="text-gray-400">{step.test_step_description}</span>
                </div>
              ))}
            </div>

            <p className="text-xs text-green-500">
              ✓ {selectedTc?.steps.length} steps ready — {selectedTc?.test_case_id}
            </p>
          </div>
        )}

        {/* Action buttons */}
        <div className="flex gap-2">
          {inputMode !== 'json' && (
            <button
              id="convert-btn"
              onClick={handleConvert}
              disabled={!canConvert || converting || isRunning}
              className="px-4 py-2 bg-gray-700 hover:bg-gray-600 disabled:opacity-40 disabled:cursor-not-allowed text-white text-sm font-medium rounded-lg transition-colors flex items-center gap-2"
            >
              {converting && (
                <svg className="w-3.5 h-3.5 animate-spin" fill="none" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8H4z" />
                </svg>
              )}
              {converting ? 'Converting…' : 'Convert'}
            </button>
          )}

          <button
            id="run-btn"
            onClick={handleStart}
            disabled={!canRun}
            className="px-4 py-2 bg-indigo-600 hover:bg-indigo-500 disabled:opacity-40 disabled:cursor-not-allowed text-white text-sm font-medium rounded-lg transition-colors"
          >
            {isStarting ? 'Starting…' : isRunning ? 'Running…' : 'Run Test'}
          </button>

          {isRunning && (
            <button
              id="stop-btn"
              onClick={handleStop}
              className="px-4 py-2 bg-red-700 hover:bg-red-600 text-white text-sm font-medium rounded-lg transition-colors"
            >
              Stop
            </button>
          )}
        </div>
      </div>

      {/* ── Blok 2 + 3 row ─────────────────────────────────────────────────── */}
      <div className="grid grid-cols-5 gap-4">

        {/* Blok 2 — Live Steps */}
        <div id="live-steps-panel" className="col-span-3 bg-gray-900 rounded-xl border border-gray-800 p-4 space-y-3">
          <div className="flex items-center justify-between">
            <h2 className="text-sm font-semibold text-gray-300 flex items-center gap-2">
              <span className="w-5 h-5 rounded-full bg-indigo-600 flex items-center justify-center text-xs text-white font-bold flex-shrink-0">2</span>
              Live Steps
            </h2>
            {totalCount > 0 && (
              <span id="steps-counter" className="text-xs text-gray-500">{completedCount} / {totalCount}</span>
            )}
          </div>

          {totalCount > 0 && (
            <div id="steps-progress-bar" className="bg-gray-800 rounded-full h-1.5 overflow-hidden">
              <div
                id="steps-progress-fill"
                className="bg-indigo-500 h-1.5 transition-all duration-500"
                style={{ width: `${progress}%` }}
              />
            </div>
          )}

          <div id="steps-list" className="space-y-0.5 max-h-80 overflow-y-auto">
            {allSteps.length === 0 ? (
              <p className="text-gray-600 text-sm text-center py-10">
                Paste a test case and click Run Test
              </p>
            ) : (
              allSteps.map((step, i) => (
                <StepItem key={i} step={step} index={i} />
              ))
            )}
          </div>
        </div>

        {/* Blok 3 — Screenshot + Downloads */}
        <div id="results-panel" className="col-span-2 bg-gray-900 rounded-xl border border-gray-800 p-4 space-y-3 flex flex-col">
          <h2 className="text-sm font-semibold text-gray-300 flex items-center gap-2">
            <span className="w-5 h-5 rounded-full bg-indigo-600 flex items-center justify-center text-xs text-white font-bold flex-shrink-0">3</span>
            Results
          </h2>

          <div id="screenshot-preview" className="bg-gray-950 rounded-lg overflow-hidden border border-gray-800 flex items-center justify-center" style={{ aspectRatio: '16/9' }}>
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

          <div id="download-buttons" className="space-y-2 flex-1">
            {runStatus?.script_path ? (
              <a
                id="download-script-btn"
                href={scriptDownloadUrl(runStatus.script_path)}
                download
                className="flex items-center gap-2.5 w-full px-3 py-2.5 bg-gray-800 hover:bg-gray-700 rounded-lg text-xs text-gray-300 transition-colors"
              >
                <svg className="w-4 h-4 text-yellow-400 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
                </svg>
                Download Playwright Script (.py)
              </a>
            ) : (
              <div className="flex items-center gap-2.5 w-full px-3 py-2.5 bg-gray-800/50 rounded-lg text-xs text-gray-700">
                <svg className="w-4 h-4 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
                </svg>
                Download Playwright Script (.py)
              </div>
            )}

            {runStatus?.report_path ? (
              <a
                id="download-report-btn"
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
