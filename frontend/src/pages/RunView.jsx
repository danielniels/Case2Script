import { useEffect, useRef, useState } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { runs } from '../api/client'

const STATUS_COLOR = {
  running: 'text-yellow-400',
  passed: 'text-green-400',
  failed: 'text-red-400',
  stopped: 'text-gray-400',
}

function StepRow({ event }) {
  if (!event || !event.step_index) return null
  const ok = event.ok !== false
  return (
    <div className={`flex items-start gap-3 py-2 border-b border-gray-800 ${event.type === 'step_end' && !ok ? 'bg-red-950/20' : ''}`}>
      <span className={`mt-0.5 font-mono text-xs w-8 shrink-0 ${ok ? 'text-green-400' : 'text-red-400'}`}>
        {event.step_index}
      </span>
      <span className="text-sm flex-1">{event.step_description || '—'}</span>
      {event.type === 'step_end' && (
        <span className={`text-xs font-semibold ${ok ? 'text-green-400' : 'text-red-400'}`}>
          {ok ? 'PASS' : 'FAIL'}
        </span>
      )}
      {event.type === 'step_start' && (
        <span className="text-xs text-yellow-400 animate-pulse">running</span>
      )}
    </div>
  )
}

export default function RunView() {
  const { runId } = useParams()
  const navigate = useNavigate()
  const [runList, setRunList] = useState([])
  const [events, setEvents] = useState([])
  const [meta, setMeta] = useState(null)
  const [screenshots, setScreenshots] = useState({})
  const esRef = useRef(null)

  useEffect(() => {
    runs.list().then(d => setRunList(d.runs || []))
  }, [])

  useEffect(() => {
    if (!runId) return
    setEvents([])
    setScreenshots({})

    runs.get(runId).then(setMeta).catch(console.error)

    const es = runs.events(runId)
    esRef.current = es

    es.onmessage = (e) => {
      const event = JSON.parse(e.data)
      setEvents(prev => [...prev, event])
      if (event.type === 'screenshot') {
        setScreenshots(prev => ({ ...prev, [event.step_index]: event.path }))
      }
      if (event.type === 'run_end' || event.type === 'done') {
        setMeta(prev => prev ? { ...prev, status: event.status } : prev)
        es.close()
      }
    }
    es.onerror = () => es.close()

    return () => es.close()
  }, [runId])

  const stepEvents = events.filter(e => e.type === 'step_start' || e.type === 'step_end')

  const mergedSteps = []
  const seen = new Set()
  for (const e of [...stepEvents].reverse()) {
    if (!seen.has(e.step_index)) {
      seen.add(e.step_index)
      mergedSteps.unshift(e)
    }
  }

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold">Runs</h1>

      {!runId && (
        <div className="space-y-2">
          {runList.length === 0 && <p className="text-gray-400">No runs yet. Start one from Suites.</p>}
          {runList.map(r => (
            <div
              key={r.run_id}
              onClick={() => navigate(`/runs/${r.run_id}`)}
              className="bg-gray-800 hover:bg-gray-700 cursor-pointer rounded-lg p-4 flex items-center justify-between"
            >
              <div>
                <p className="font-mono text-sm">{r.run_id}</p>
                <p className="text-xs text-gray-400">{r.test_case_id} · {r.total_steps} steps</p>
              </div>
              <span className={`text-sm font-semibold ${STATUS_COLOR[r.status] || 'text-gray-300'}`}>
                {r.status}
              </span>
            </div>
          ))}
        </div>
      )}

      {runId && (
        <div className="space-y-4">
          <div className="flex items-center gap-4">
            <button onClick={() => navigate('/runs')} className="text-indigo-400 text-sm underline">
              ← All runs
            </button>
            {meta && (
              <>
                <span className="font-mono text-sm text-gray-400">{runId}</span>
                <span className={`font-bold ${STATUS_COLOR[meta.status] || 'text-gray-300'}`}>
                  {meta.status}
                </span>
                {meta.status === 'running' && (
                  <button
                    onClick={() => runs.stop(runId)}
                    className="bg-red-800 hover:bg-red-700 px-3 py-1 rounded text-xs"
                  >
                    Stop
                  </button>
                )}
              </>
            )}
          </div>

          {/* Progress bar */}
          {meta && (
            <div className="bg-gray-800 rounded-full h-2 overflow-hidden">
              <div
                className="bg-indigo-500 h-2 transition-all"
                style={{ width: `${((meta.current_step || 0) / (meta.total_steps || 1)) * 100}%` }}
              />
            </div>
          )}

          {/* Step list */}
          <div className="bg-gray-900 rounded-lg overflow-hidden">
            <div className="px-4 py-2 border-b border-gray-800 text-xs text-gray-400 font-semibold uppercase">
              Steps
            </div>
            {mergedSteps.length === 0 && (
              <p className="px-4 py-3 text-gray-500 text-sm">Waiting for steps…</p>
            )}
            <div className="px-4 divide-y divide-gray-800/50">
              {mergedSteps.map((e, i) => (
                <div key={i}>
                  <StepRow event={e} />
                  {screenshots[e.step_index] && (
                    <img
                      src={`/data/saved_screenshots/${screenshots[e.step_index].split('/').slice(-2).join('/')}`}
                      alt={`Step ${e.step_index} screenshot`}
                      className="mt-1 mb-2 rounded border border-gray-700 max-h-48 object-contain"
                      onError={ev => ev.target.style.display = 'none'}
                    />
                  )}
                </div>
              ))}
            </div>
          </div>

          {/* Report / script links */}
          {meta?.report_path && (
            <div className="bg-gray-800 rounded p-3 text-sm space-y-1">
              <p className="text-gray-400">Report: <span className="text-gray-200 font-mono">{meta.report_path}</span></p>
              {meta.script_path && (
                <p className="text-gray-400">
                  Script: <span className="text-gray-200 font-mono">{meta.script_path}</span>
                  {' '}
                  <button
                    onClick={() => navigate(`/scripts/${encodeURIComponent(meta.script_path)}`)}
                    className="text-indigo-400 underline ml-2"
                  >
                    Edit
                  </button>
                </p>
              )}
            </div>
          )}
        </div>
      )}
    </div>
  )
}
