import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { runs } from '../api/client'

function StatusBadge({ status }) {
  const cls =
    status === 'passed'  ? 'bg-green-900/60 text-green-300 border border-green-700' :
    status === 'failed'  ? 'bg-red-900/60 text-red-300 border border-red-700' :
    status === 'running' ? 'bg-blue-900/60 text-blue-300 border border-blue-700' :
    status === 'stopped' ? 'bg-yellow-900/60 text-yellow-300 border border-yellow-700' :
    'bg-gray-800 text-gray-400 border border-gray-700'
  return (
    <span className={`inline-block text-xs font-semibold px-2 py-0.5 rounded-full ${cls}`}>
      {(status || 'unknown').replace('_', ' ').toUpperCase()}
    </span>
  )
}

function formatDate(ts) {
  if (!ts) return '—'
  try {
    const d = new Date(ts)
    return isNaN(d.getTime()) ? String(ts) : d.toLocaleString()
  } catch {
    return String(ts)
  }
}

export default function HistoryPage() {
  const [list, setList] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [deleting, setDeleting] = useState(null)
  const navigate = useNavigate()

  const load = () => {
    setLoading(true)
    setError(null)
    runs.list()
      .then(data => {
        setList(data.runs || [])
        setLoading(false)
      })
      .catch(err => {
        setError(err.message || 'Failed to load history')
        setLoading(false)
      })
  }

  const handleRerun = async (e, run) => {
    e.stopPropagation()

    // Restore original prompt if available
    if (run.input_mode === 'prompt' && run.input_content) {
      navigate('/', { state: { rerunMode: 'prompt', rerunContent: run.input_content } })
      return
    }

    // Restore original JSON if available
    if (run.input_mode === 'json' && run.input_content) {
      navigate('/', { state: { rerunJson: run.input_content } })
      return
    }

    // Fallback: reconstruct JSON from stored steps
    let steps = []
    try {
      const res = await runs.steps(run.run_id)
      steps = (res.steps || []).sort((a, b) => a.step_index - b.step_index)
    } catch { /* proceed without steps */ }

    const payload = {
      suite_id: run.suite_id || '',
      test_case_id: run.test_case_id || '',
      test_case_name: run.test_case_name || '',
      test_data: {},
      steps: steps.map(s => ({
        test_step_id: String(s.step_index),
        test_step_description: s.description,
      })),
    }
    navigate('/', { state: { rerunJson: JSON.stringify(payload, null, 2) } })
  }

  const handleDelete = async (e, runId) => {
    e.stopPropagation()
    if (!window.confirm(`Delete run ${runId}?`)) return
    setDeleting(runId)
    try {
      await runs.delete(runId)
      setList(prev => prev.filter(r => r.run_id !== runId))
    } catch (err) {
      alert(err.message || 'Failed to delete')
    } finally {
      setDeleting(null)
    }
  }

  useEffect(() => { load() }, [])

  return (
    <div className="p-6 space-y-4">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-xl font-semibold text-white">Run History</h1>
          <p className="text-xs text-gray-500 mt-0.5">All past runs — click a row to view details</p>
        </div>
        <button
          onClick={load}
          disabled={loading}
          className="flex items-center gap-1.5 px-3 py-1.5 bg-gray-800 hover:bg-gray-700 rounded-lg text-xs text-gray-300 transition-colors disabled:opacity-50"
        >
          <svg className={`w-3.5 h-3.5 ${loading ? 'animate-spin' : ''}`} fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
          </svg>
          Refresh
        </button>
      </div>

      {/* Error */}
      {error && (
        <div className="bg-red-950/30 border border-red-800/50 rounded-xl px-4 py-3 text-sm text-red-400">
          {error}
        </div>
      )}

      {/* Table */}
      <div className="bg-gray-900 rounded-xl border border-gray-800 overflow-hidden">
        <table className="w-full text-sm table-fixed">
          <colgroup>
            <col className="w-32" />
            <col />
            <col className="w-40" />
            <col className="w-24" />
            <col className="w-20" />
            <col className="w-24" />
            <col className="w-20" />
          </colgroup>
          <thead>
            <tr className="border-b border-gray-800">
              <th className="text-left px-4 py-3 text-xs text-gray-500 font-semibold uppercase">Run ID</th>
              <th className="text-left px-4 py-3 text-xs text-gray-500 font-semibold uppercase">Test Case</th>
              <th className="text-left px-4 py-3 text-xs text-gray-500 font-semibold uppercase">Started</th>
              <th className="text-left px-4 py-3 text-xs text-gray-500 font-semibold uppercase">Steps</th>
              <th className="text-left px-4 py-3 text-xs text-gray-500 font-semibold uppercase">Status</th>
              <th className="text-left px-4 py-3 text-xs text-gray-500 font-semibold uppercase">Suite</th>
              <th className="w-12" />
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-800/50">
            {loading ? (
              <tr>
                <td colSpan={6} className="px-4 py-10 text-center text-gray-600 text-sm">
                  Loading…
                </td>
              </tr>
            ) : list.length === 0 ? (
              <tr>
                <td colSpan={7} className="px-4 py-10 text-center text-gray-600 text-sm">
                  No runs yet. Go to <span className="text-indigo-400">Run Test</span> to start one.
                </td>
              </tr>
            ) : (
              list.map(run => (
                <tr
                  key={run.run_id}
                  onClick={() => navigate(`/runs/${run.run_id}`)}
                  className="cursor-pointer transition-colors hover:bg-gray-800/40 group"
                >
                  <td className="px-4 py-3 font-mono text-xs text-gray-500">{run.run_id}</td>
                  <td className="px-4 py-3">
                    <span className="block text-gray-200 text-sm font-medium truncate">
                      {run.test_case_name || run.test_case_id}
                    </span>
                    {run.test_case_name && run.test_case_id !== run.test_case_name && (
                      <span className="block text-xs text-gray-600 font-mono truncate">
                        {run.test_case_id}
                      </span>
                    )}
                  </td>
                  <td className="px-4 py-3 text-xs text-gray-400">{formatDate(run.started_at)}</td>
                  <td className="px-4 py-3 text-xs text-gray-400">
                    {run.current_step != null && run.total_steps
                      ? `${run.current_step}/${run.total_steps}`
                      : run.total_steps ?? '—'}
                  </td>
                  <td className="px-4 py-3">
                    <StatusBadge status={run.status} />
                  </td>
                  <td className="px-4 py-3 text-xs text-gray-600 font-mono truncate">
                    {run.suite_id || '—'}
                  </td>
                  <td className="px-4 py-3">
                    <div className="flex items-center justify-end gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
                      {/* Re-run */}
                      <button
                        onClick={(e) => handleRerun(e, run)}
                        title="Re-run this test case"
                        className="p-1 rounded text-gray-600 hover:text-green-400 hover:bg-green-950/30"
                      >
                        <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M14.752 11.168l-3.197-2.132A1 1 0 0010 9.87v4.263a1 1 0 001.555.832l3.197-2.132a1 1 0 000-1.664z" />
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                        </svg>
                      </button>
                      {/* Delete */}
                      <button
                        onClick={(e) => handleDelete(e, run.run_id)}
                        disabled={deleting === run.run_id || run.status === 'running'}
                        title={run.status === 'running' ? 'Stop the run first' : 'Delete run'}
                        className="p-1 rounded text-gray-600 hover:text-red-400 hover:bg-red-950/30 disabled:opacity-30 disabled:cursor-not-allowed"
                      >
                        {deleting === run.run_id ? (
                          <svg className="w-4 h-4 animate-spin" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                          </svg>
                        ) : (
                          <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                          </svg>
                        )}
                      </button>
                    </div>
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </div>
  )
}
