import { useEffect, useRef, useState } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { runs, screenshotUrl, scriptDownloadUrl, reportViewUrl } from '../api/client'

function StatusBadge({ status }) {
  const cls =
    status === 'passed'    ? 'bg-green-900/60 text-green-300 border border-green-700' :
    status === 'failed'    ? 'bg-red-900/60 text-red-300 border border-red-700' :
    status === 'running'   ? 'bg-blue-900/60 text-blue-300 border border-blue-700' :
    status === 'not_found' ? 'bg-yellow-900/60 text-yellow-300 border border-yellow-700' :
    'bg-gray-800 text-gray-400 border border-gray-700'
  return (
    <span className={`inline-block text-xs font-semibold px-2 py-0.5 rounded-full ${cls}`}>
      {(status || 'unknown').replace('_', ' ').toUpperCase()}
    </span>
  )
}

function StepStatusBadge({ status }) {
  if (status === 'passed')  return <span className="text-xs font-semibold text-green-400">PASS</span>
  if (status === 'failed')  return <span className="text-xs font-semibold text-red-400">FAIL</span>
  if (status === 'running') return <span className="text-xs font-semibold text-blue-400 animate-pulse">running</span>
  return <span className="text-xs text-gray-600">—</span>
}

export default function RunDetailPage() {
  const { runId } = useParams()
  const navigate = useNavigate()
  const [meta, setMeta] = useState(null)
  const [stepMap, setStepMap] = useState({})
  const [lightbox, setLightbox] = useState(null)
  const [loading, setLoading] = useState(true)
  const [notFound, setNotFound] = useState(false)
  const esRef = useRef(null)

  useEffect(() => {
    if (!runId) return

    setLoading(true)
    setNotFound(false)
    setMeta(null)
    setStepMap({})

    // Always check if run exists FIRST — never subscribe to SSE for a dead runId.
    runs.get(runId)
      .then(data => {
        setMeta(data)
        setLoading(false)

        // Pre-load any cached step data from this session
        const cached = localStorage.getItem(`run_steps_${runId}`)
        const tempMap = cached ? (() => { try { return JSON.parse(cached) } catch { return {} } })() : {}
        if (cached) setStepMap(tempMap)

        // Subscribe to SSE — replays all past events for finished runs,
        // streams live events for running ones.
        const es = runs.events(runId)
        esRef.current = es

        es.onmessage = (e) => {
          let ev
          try { ev = JSON.parse(e.data) } catch { return }

          if (ev.type === 'step_start') {
            tempMap[ev.step_index] = {
              description: ev.step_description,
              status: 'running',
              screenshot_path: null,
              error: null,
            }
            setStepMap({ ...tempMap })
          } else if (ev.type === 'step_end') {
            tempMap[ev.step_index] = {
              description: ev.step_description,
              status: ev.ok ? 'passed' : 'failed',
              screenshot_path: ev.screenshot_path || null,
              error: ev.error || null,
            }
            setStepMap({ ...tempMap })
            localStorage.setItem(`run_steps_${runId}`, JSON.stringify(tempMap))
          } else if (ev.type === 'run_end' || ev.type === 'done') {
            localStorage.setItem(`run_steps_${runId}`, JSON.stringify(tempMap))
            runs.get(runId).then(setMeta).catch(() => {})
            es.close()
          } else if (ev.type === 'critical_failure') {
            setMeta(prev => prev ? { ...prev, status: 'failed' } : null)
          }
        }

        es.onerror = () => {
          es.close()
          esRef.current = null
        }
      })
      .catch(err => {
        setLoading(false)
        if (err.status === 404) {
          setNotFound(true)
        } else {
          setMeta({ status: 'error', error: err.message })
        }
      })

    return () => {
      if (esRef.current) {
        esRef.current.close()
        esRef.current = null
      }
    }
  }, [runId])

  const stepsArray = Object.entries(stepMap)
    .sort(([a], [b]) => Number(a) - Number(b))
    .map(([index, step]) => ({ index: Number(index), ...step }))

  const passCount = stepsArray.filter(s => s.status === 'passed').length
  const failCount = stepsArray.filter(s => s.status === 'failed').length

  if (loading) {
    return (
      <div className="p-6 flex items-center justify-center h-64">
        <p className="text-gray-500 text-sm">Loading…</p>
      </div>
    )
  }

  if (notFound) {
    return (
      <div className="p-6 space-y-4">
        <div className="flex items-center justify-between">
          <h1 className="text-xl font-semibold text-white">Run Detail</h1>
          <button onClick={() => navigate('/')} className="text-xs text-indigo-400 hover:text-indigo-300">
            ← Run Test
          </button>
        </div>
        <div className="bg-gray-900 border border-yellow-800/50 rounded-xl p-6 text-center space-y-2">
          <p className="text-yellow-400 font-semibold text-sm">Run not found</p>
          <p className="text-gray-500 text-xs font-mono">{runId}</p>
          <p className="text-gray-600 text-xs">
            This run no longer exists in server memory (server may have restarted). Go back and start a new run.
          </p>
        </div>
      </div>
    )
  }

  return (
    <div className="p-6 space-y-4">
      {/* Header */}
      <div className="flex items-start justify-between gap-4">
        <div className="space-y-1">
          <h1 className="text-xl font-semibold text-white">Run Detail</h1>
          <p className="text-xs text-gray-500 font-mono">{runId}</p>
          {meta?.test_case_name && (
            <p className="text-sm text-gray-400">{meta.test_case_name}</p>
          )}
        </div>
        <div className="flex items-center gap-3 flex-shrink-0">
          {meta && <StatusBadge status={meta.status} />}
          <button
            onClick={() => navigate('/')}
            className="text-xs text-indigo-400 hover:text-indigo-300 transition-colors"
          >
            ← Run Test
          </button>
        </div>
      </div>

      {/* Stats row */}
      <div className="flex gap-4 text-xs text-gray-500">
        {meta && (
          <>
            <span>Total: <span className="text-gray-300">{meta.total_steps || stepsArray.length} steps</span></span>
            <span>Pass: <span className="text-green-400 font-semibold">{passCount}</span></span>
            <span>Fail: <span className={failCount > 0 ? 'text-red-400 font-semibold' : 'text-gray-500'}>{failCount}</span></span>
            {meta.started_at && (
              <span>Started: <span className="text-gray-300">{formatTime(meta.started_at)}</span></span>
            )}
          </>
        )}
      </div>

      {/* Downloads */}
      {meta && (meta.script_path || meta.report_path) && (
        <div className="flex gap-2">
          {meta.script_path && (
            <a
              href={scriptDownloadUrl(meta.script_path)}
              download
              className="flex items-center gap-1.5 px-3 py-1.5 bg-gray-800 hover:bg-gray-700 rounded-lg text-xs text-gray-300 transition-colors"
            >
              <svg className="w-3.5 h-3.5 text-yellow-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
              </svg>
              Playwright Script
            </a>
          )}
          {meta.report_path && (
            <a
              href={reportViewUrl(meta.report_path)}
              download
              className="flex items-center gap-1.5 px-3 py-1.5 bg-gray-800 hover:bg-gray-700 rounded-lg text-xs text-gray-300 transition-colors"
            >
              <svg className="w-3.5 h-3.5 text-green-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
              </svg>
              Test Report
            </a>
          )}
        </div>
      )}

      {/* Step table */}
      <div className="bg-gray-900 rounded-xl border border-gray-800 overflow-hidden">
        <table className="w-full text-sm table-fixed">
          <colgroup>
            <col className="w-10" />
            <col />
            <col className="w-28" />
            <col className="w-20" />
          </colgroup>
          <thead>
            <tr className="border-b border-gray-800">
              <th className="text-left px-4 py-3 text-xs text-gray-500 font-semibold uppercase">#</th>
              <th className="text-left px-4 py-3 text-xs text-gray-500 font-semibold uppercase">Description</th>
              <th className="text-left px-4 py-3 text-xs text-gray-500 font-semibold uppercase">Screenshot</th>
              <th className="text-left px-4 py-3 text-xs text-gray-500 font-semibold uppercase">Status</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-800/50">
            {stepsArray.length === 0 ? (
              <tr>
                <td colSpan={4} className="px-4 py-10 text-center text-gray-600 text-sm">
                  No step data available.
                </td>
              </tr>
            ) : (
              stepsArray.map(step => (
                <tr
                  key={step.index}
                  className={`transition-colors ${
                    step.status === 'failed'  ? 'bg-red-950/10 hover:bg-red-950/20' :
                    step.status === 'running' ? 'bg-blue-950/10' :
                    'hover:bg-gray-800/30'
                  }`}
                >
                  <td className="px-4 py-3 text-gray-500 font-mono text-xs">{step.index}</td>
                  <td className="px-4 py-3">
                    <span className="block text-gray-300 text-sm">{step.description}</span>
                    {step.error && (
                      <span className="block text-xs text-red-400 mt-0.5 font-mono truncate" title={step.error}>
                        {step.error}
                      </span>
                    )}
                  </td>
                  <td className="px-4 py-3">
                    {step.screenshot_path ? (
                      <button
                        onClick={() => setLightbox(step.screenshot_path)}
                        className="block w-20 h-12 overflow-hidden rounded border border-gray-700 hover:border-indigo-500 transition-colors focus:outline-none"
                        title="Click to enlarge"
                      >
                        <img
                          src={screenshotUrl(step.screenshot_path)}
                          alt={`Step ${step.index}`}
                          className="w-full h-full object-cover"
                          onError={ev => { ev.target.parentElement.style.display = 'none' }}
                        />
                      </button>
                    ) : (
                      <span className="text-gray-700 text-xs">—</span>
                    )}
                  </td>
                  <td className="px-4 py-3">
                    <StepStatusBadge status={step.status} />
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>

      {/* Lightbox */}
      {lightbox && (
        <div
          className="fixed inset-0 bg-black/85 flex items-center justify-center z-50 p-6"
          onClick={() => setLightbox(null)}
        >
          <div className="relative max-w-5xl w-full" onClick={e => e.stopPropagation()}>
            <button
              onClick={() => setLightbox(null)}
              className="absolute -top-8 right-0 text-gray-400 hover:text-white text-sm"
            >
              Close ✕
            </button>
            <img
              src={screenshotUrl(lightbox)}
              alt="Step screenshot"
              className="max-w-full max-h-[85vh] object-contain rounded-xl shadow-2xl mx-auto block"
            />
          </div>
        </div>
      )}
    </div>
  )
}

function formatTime(ts) {
  if (!ts) return ''
  try {
    const d = typeof ts === 'number' ? new Date(ts * 1000) : new Date(ts)
    return isNaN(d.getTime()) ? String(ts) : d.toLocaleTimeString()
  } catch {
    return String(ts)
  }
}
