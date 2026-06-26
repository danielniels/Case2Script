import { useEffect, useState } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { scripts } from '../api/client'

function Spinner() {
  return (
    <svg className="w-3.5 h-3.5 animate-spin" fill="none" viewBox="0 0 24 24">
      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8H4z" />
    </svg>
  )
}

export default function ScriptEditor() {
  const { scriptPath } = useParams()
  const navigate = useNavigate()
  const decoded = decodeURIComponent(scriptPath || '')

  const [code, setCode]             = useState('')
  const [loading, setLoading]       = useState(true)
  const [saving, setSaving]         = useState(false)
  const [toast, setToast]           = useState(null)   // { type: 'success'|'error', msg }
  const [edited, setEdited]         = useState(false)

  // Run state
  const [running, setRunning]       = useState(false)
  const [runResult, setRunResult]   = useState(null)   // { ok, exit_code, stdout, stderr, screenshot_dir, timed_out }
  const [screenshots, setScreenshots] = useState([])   // [{ name, url }]
  const [logExpanded, setLogExpanded] = useState(true)
  const [lightbox, setLightbox]     = useState(null)   // url string

  useEffect(() => {
    if (!decoded) return
    setLoading(true)
    scripts.get(decoded)
      .then(d => { setCode(d.content || ''); setLoading(false) })
      .catch(err => {
        setCode('# Could not load script')
        setLoading(false)
        showToast('error', err.message || 'Failed to load script')
      })
  }, [decoded])

  function showToast(type, msg) {
    setToast({ type, msg })
    setTimeout(() => setToast(null), 3500)
  }

  // Returns true on success, false on failure. Does NOT show a toast (caller decides).
  async function _saveFile() {
    setSaving(true)
    try {
      await scripts.save(decoded, code)
      setEdited(false)
      return true
    } catch (err) {
      showToast('error', err.message || 'Save failed')
      return false
    } finally {
      setSaving(false)
    }
  }

  async function handleSave() {
    const ok = await _saveFile()
    if (ok) showToast('success', 'Script saved successfully')
  }

  async function handleRun() {
    // Auto-save unsaved edits before running so the file on disk is current
    if (edited) {
      const saved = await _saveFile()
      if (!saved) return
    }

    setRunning(true)
    setRunResult(null)
    setScreenshots([])

    try {
      const result = await scripts.run(decoded)
      setRunResult(result)
      if (result.screenshot_dir) {
        try {
          const ssData = await scripts.screenshots(result.screenshot_dir)
          setScreenshots(ssData.screenshots || [])
        } catch {
          // Non-fatal: just no screenshots shown
        }
      }
    } catch (err) {
      setRunResult({
        ok: false,
        exit_code: -1,
        stdout: '',
        stderr: err.message || 'Run request failed',
        screenshot_dir: null,
        timed_out: false,
      })
    } finally {
      setRunning(false)
    }
  }

  const filename = decoded.replace(/\\/g, '/').split('/').pop()
  const logOutput = [
    runResult?.stdout,
    runResult?.stderr ? '--- stderr ---\n' + runResult.stderr : '',
  ].filter(Boolean).join('\n').trim()

  return (
    <div className="p-6 space-y-4 min-h-screen bg-gray-950 text-gray-100">

      {/* Header */}
      <div className="flex items-center gap-3 flex-wrap">
        <button
          onClick={() => navigate(-1)}
          className="text-indigo-400 hover:text-indigo-300 text-sm transition-colors"
        >
          ← Back
        </button>
        <h1 className="text-lg font-semibold font-mono text-white truncate flex-1">{filename}</h1>
        {edited && (
          <span className="text-xs bg-yellow-900/60 text-yellow-300 border border-yellow-700/60 px-2 py-0.5 rounded-full">
            Unsaved changes
          </span>
        )}
      </div>

      {/* Toast */}
      {toast && (
        <div
          className={`flex items-center gap-2 px-4 py-2.5 rounded-lg text-sm border ${
            toast.type === 'success'
              ? 'bg-green-900/50 border-green-700/60 text-green-300'
              : 'bg-red-900/50 border-red-700/60 text-red-300'
          }`}
        >
          {toast.type === 'success' ? '✓' : '✕'} {toast.msg}
        </div>
      )}

      {/* Editor */}
      {loading ? (
        <div className="h-[60vh] flex items-center justify-center">
          <p className="text-gray-500 text-sm">Loading script…</p>
        </div>
      ) : (
        <textarea
          className={`w-full bg-gray-900 text-green-300 font-mono text-xs rounded-lg p-4 resize-none border border-gray-700 focus:outline-none focus:border-indigo-500 transition-colors leading-relaxed ${
            runResult ? 'h-[40vh]' : 'h-[65vh]'
          }`}
          value={code}
          onChange={e => { setCode(e.target.value); setEdited(true) }}
          spellCheck={false}
          autoComplete="off"
          autoCorrect="off"
          autoCapitalize="off"
        />
      )}

      {/* Action bar */}
      <div className="flex items-center gap-3 flex-wrap">
        <button
          disabled={saving || loading || running}
          onClick={handleSave}
          className="flex items-center gap-2 px-4 py-2 bg-indigo-600 hover:bg-indigo-500 disabled:opacity-50 disabled:cursor-not-allowed rounded-lg text-sm font-medium transition-colors"
        >
          {saving ? <><Spinner /> Saving…</> : 'Save'}
        </button>

        <button
          disabled={running || loading}
          onClick={handleRun}
          className="flex items-center gap-2 px-4 py-2 disabled:opacity-50 disabled:cursor-not-allowed rounded-lg text-sm font-medium text-white transition-opacity hover:opacity-90"
          style={{ background: (running || loading) ? '#4c3b7a' : '#7C5CD6' }}
        >
          {running ? (
            <><Spinner /> Running…</>
          ) : (
            <>
              <svg className="w-3.5 h-3.5" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM9.555 7.168A1 1 0 008 8v4a1 1 0 001.555.832l3-2a1 1 0 000-1.664l-3-2z" clipRule="evenodd" />
              </svg>
              Run
            </>
          )}
        </button>

        <a
          href={scripts.downloadUrl(decoded)}
          download={filename}
          className="flex items-center gap-1.5 px-4 py-2 bg-gray-800 hover:bg-gray-700 rounded-lg text-sm text-gray-300 transition-colors"
        >
          <svg className="w-3.5 h-3.5 text-yellow-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2}
              d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
          </svg>
          Download .py
        </a>

        <span className="text-xs text-gray-600 ml-auto font-mono truncate hidden sm:block">{decoded}</span>
      </div>

      {/* Results panel */}
      {runResult && (
        <div className="space-y-3">

          {/* PASS / FAIL badge */}
          <div
            className={`flex items-center gap-2.5 px-4 py-3 rounded-lg border text-sm font-semibold ${
              runResult.ok
                ? 'border-[#1A9E5C]/50 text-[#1A9E5C]'
                : 'border-[#E03E3E]/50 text-[#E03E3E]'
            }`}
            style={{
              background: runResult.ok ? 'rgba(26,158,92,0.12)' : 'rgba(224,62,62,0.12)',
            }}
          >
            {runResult.ok ? (
              <>
                <svg className="w-4 h-4 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2.5} d="M5 13l4 4L19 7" />
                </svg>
                PASS
              </>
            ) : (
              <>
                <svg className="w-4 h-4 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2.5} d="M6 18L18 6M6 6l12 12" />
                </svg>
                FAIL
                {runResult.timed_out && ' — timed out'}
                {!runResult.timed_out && runResult.exit_code != null && runResult.exit_code !== -1
                  && ` (exit ${runResult.exit_code})`}
              </>
            )}
          </div>

          {/* Output log */}
          <div className="border border-gray-700 rounded-lg overflow-hidden">
            <button
              onClick={() => setLogExpanded(v => !v)}
              className="w-full flex items-center justify-between px-4 py-2.5 bg-gray-800 hover:bg-gray-700 text-xs text-gray-400 transition-colors"
            >
              <span className="font-semibold uppercase tracking-wide">Output log</span>
              <svg
                className={`w-4 h-4 transition-transform ${logExpanded ? 'rotate-180' : ''}`}
                fill="none" viewBox="0 0 24 24" stroke="currentColor"
              >
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
              </svg>
            </button>
            {logExpanded && (
              <pre className="p-4 font-mono text-xs text-gray-300 bg-gray-900 overflow-auto max-h-56 whitespace-pre-wrap break-words">
                {logOutput || '(no output)'}
              </pre>
            )}
          </div>

          {/* Screenshot gallery */}
          {screenshots.length > 0 && (
            <div className="space-y-2">
              <p className="text-xs text-gray-500 font-semibold uppercase tracking-wide">
                Screenshots ({screenshots.length})
              </p>
              <div className="grid grid-cols-4 gap-2">
                {screenshots.map(ss => (
                  <button
                    key={ss.name}
                    onClick={() => setLightbox(ss.url)}
                    className="aspect-video rounded border border-gray-700 hover:border-indigo-500 overflow-hidden transition-colors focus:outline-none"
                    title={ss.name}
                  >
                    <img
                      src={ss.url}
                      alt={ss.name}
                      className="w-full h-full object-cover"
                      onError={e => { e.target.parentElement.style.display = 'none' }}
                    />
                  </button>
                ))}
              </div>
            </div>
          )}

          {screenshots.length === 0 && runResult.screenshot_dir && !running && (
            <p className="text-xs text-gray-600 font-mono">{runResult.screenshot_dir} — no screenshots</p>
          )}
        </div>
      )}

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
              src={lightbox}
              alt="Screenshot"
              className="max-w-full max-h-[85vh] object-contain rounded-xl shadow-2xl mx-auto block"
            />
          </div>
        </div>
      )}

    </div>
  )
}
