import { useEffect, useState } from 'react'
import { useParams, useNavigate } from 'react-router-dom'

/**
 * Stage 3: Edit the generated .js Playwright script.
 * Uses a plain <textarea> (Monaco/CodeMirror integration is a v2 upgrade).
 * Once the user edits the script, regenerate-from-JSON is locked.
 */
export default function ScriptEditor() {
  const { scriptPath } = useParams()
  const navigate = useNavigate()
  const [code, setCode] = useState('')
  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState(false)
  const [edited, setEdited] = useState(false)
  const [saved, setSaved] = useState(false)
  const decoded = decodeURIComponent(scriptPath || '')

  useEffect(() => {
    if (!decoded) return
    fetch(`/api/scripts?path=${encodeURIComponent(decoded)}`)
      .then(r => r.json())
      .then(d => { setCode(d.content || ''); setLoading(false) })
      .catch(() => { setCode('// Could not load script'); setLoading(false) })
  }, [decoded])

  const handleSave = async () => {
    setSaving(true)
    try {
      await fetch('/api/scripts', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ path: decoded, content: code }),
      })
      setSaved(true)
      setTimeout(() => setSaved(false), 2000)
    } catch (e) {
      alert(`Save failed: ${e.message}`)
    } finally {
      setSaving(false)
    }
  }

  const handleChange = (e) => {
    setCode(e.target.value)
    setEdited(true)
  }

  return (
    <div id="script-editor-page" className="space-y-4">
      <div className="flex items-center gap-4">
        <button id="script-back-btn" onClick={() => navigate(-1)} className="text-indigo-400 text-sm underline">← Back</button>
        <h1 className="text-xl font-bold font-mono truncate">{decoded.split('/').pop()}</h1>
        {edited && (
          <span className="text-xs bg-yellow-700 text-yellow-100 px-2 py-0.5 rounded">
            Edited — regenerate-from-JSON locked
          </span>
        )}
      </div>

      {loading ? (
        <p className="text-gray-400">Loading…</p>
      ) : (
        <textarea
          id="script-code-textarea"
          className="w-full h-[70vh] bg-gray-900 text-green-300 font-mono text-xs rounded p-3 resize-none border border-gray-700 focus:outline-none focus:border-indigo-500"
          value={code}
          onChange={handleChange}
          spellCheck={false}
        />
      )}

      <div className="flex gap-3">
        <button
          id="script-save-btn"
          disabled={saving || loading}
          onClick={handleSave}
          className="bg-indigo-600 hover:bg-indigo-500 disabled:opacity-50 px-4 py-2 rounded text-sm"
        >
          {saving ? 'Saving…' : saved ? 'Saved ✓' : 'Save'}
        </button>
        <a
          id="script-download-link"
          href={`/api/scripts/download?path=${encodeURIComponent(decoded)}`}
          className="bg-gray-700 hover:bg-gray-600 px-4 py-2 rounded text-sm"
        >
          Download .js
        </a>
      </div>
    </div>
  )
}
