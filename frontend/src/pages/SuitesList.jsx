import { useEffect, useState } from 'react'
import { suites, converters, runs } from '../api/client'

export default function SuitesList() {
  const [list, setList] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [jsonInput, setJsonInput] = useState('')
  const [promptText, setPromptText] = useState('')
  const [importing, setImporting] = useState(false)
  const [runningId, setRunningId] = useState(null)
  const [runResult, setRunResult] = useState(null)

  const load = async () => {
    setLoading(true)
    try {
      const data = await suites.list()
      setList(data.suites || [])
    } catch (e) {
      setError(e.message)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => { load() }, [])

  const handleRunSuite = async (suite) => {
    const full = await suites.get(suite.id)
    const testCase = full.test_cases?.[0]
    if (!testCase) return alert('No test cases in this suite')
    setRunningId(suite.id)
    try {
      const result = await runs.start({
        suite_id: suite.id,
        test_case_id: testCase.test_case_id,
        steps: testCase.steps || [],
      })
      setRunResult(result)
      window.location.href = `/runs/${result.run_id}`
    } catch (e) {
      alert(`Run failed: ${e.message}`)
    } finally {
      setRunningId(null)
    }
  }

  const handleJsonImport = async () => {
    setImporting(true)
    try {
      const parsed = JSON.parse(jsonInput)
      const suite = await converters.fromJson(parsed)
      await suites.create(suite)
      setJsonInput('')
      load()
    } catch (e) {
      alert(`Import failed: ${e.message}`)
    } finally {
      setImporting(false)
    }
  }

  const handleExcelImport = async (e) => {
    const file = e.target.files?.[0]
    if (!file) return
    setImporting(true)
    try {
      const suite = await converters.fromExcel(file)
      await suites.create(suite)
      load()
    } catch (err) {
      alert(`Excel import failed: ${err.message}`)
    } finally {
      setImporting(false)
      e.target.value = ''
    }
  }

  const handlePromptImport = async () => {
    if (!promptText.trim()) return
    setImporting(true)
    try {
      const suite = await converters.fromPrompt(promptText)
      await suites.create(suite)
      setPromptText('')
      load()
    } catch (e) {
      alert(`Prompt import failed: ${e.message}`)
    } finally {
      setImporting(false)
    }
  }

  const handleDelete = async (id) => {
    if (!confirm(`Delete suite ${id}?`)) return
    await suites.delete(id)
    load()
  }

  return (
    <div id="suites-page" className="space-y-6">
      <h1 className="text-2xl font-bold">Test Suites</h1>

      {/* Import panel */}
      <div id="import-panel" className="bg-gray-800 rounded-lg p-4 space-y-4">
        <h2 className="font-semibold text-lg">Import Suite</h2>

        {/* JSON */}
        <div className="space-y-2">
          <label className="text-sm text-gray-400">Paste JSON suite</label>
          <textarea
            id="json-suite-textarea"
            className="w-full h-32 bg-gray-900 rounded p-2 text-sm font-mono text-green-400 resize-y"
            placeholder='{"id": "...", "test_cases": [...]}'
            value={jsonInput}
            onChange={e => setJsonInput(e.target.value)}
          />
          <button
            id="import-json-btn"
            disabled={importing || !jsonInput}
            onClick={handleJsonImport}
            className="bg-indigo-600 hover:bg-indigo-500 disabled:opacity-50 px-4 py-1.5 rounded text-sm"
          >
            {importing ? 'Importing…' : 'Import JSON'}
          </button>
        </div>

        {/* Excel */}
        <div className="flex items-center gap-3">
          <label className="text-sm text-gray-400">Upload Excel</label>
          <input id="excel-upload-input" type="file" accept=".xlsx,.xls" onChange={handleExcelImport} className="text-sm" />
          <a id="excel-template-link" href={converters.excelTemplate()} className="text-indigo-400 text-sm underline">
            Download template
          </a>
        </div>

        {/* Prompt */}
        <div className="space-y-2">
          <label className="text-sm text-gray-400">Generate from prompt (Ollama)</label>
          <textarea
            id="prompt-textarea"
            className="w-full h-20 bg-gray-900 rounded p-2 text-sm resize-y"
            placeholder="Describe the test scenario in plain text…"
            value={promptText}
            onChange={e => setPromptText(e.target.value)}
          />
          <button
            id="generate-ai-btn"
            disabled={importing || !promptText.trim()}
            onClick={handlePromptImport}
            className="bg-purple-700 hover:bg-purple-600 disabled:opacity-50 px-4 py-1.5 rounded text-sm"
          >
            {importing ? 'Generating…' : 'Generate with AI'}
          </button>
        </div>
      </div>

      {/* Suite list */}
      {loading && <p className="text-gray-400">Loading…</p>}
      {error && <p className="text-red-400">{error}</p>}
      {!loading && list.length === 0 && (
        <p className="text-gray-400">No suites yet. Import one above.</p>
      )}
      <div id="suites-list" className="space-y-3">
        {list.map(s => (
          <div key={s.id} id={`suite-${s.id}`} className="bg-gray-800 rounded-lg p-4 flex items-center justify-between">
            <div>
              <p className="font-medium">{s.name}</p>
              <p className="text-sm text-gray-400">
                {s.test_case_count} test case{s.test_case_count !== 1 ? 's' : ''} · {s.id}
              </p>
              {s.description && <p className="text-xs text-gray-500 mt-1">{s.description}</p>}
            </div>
            <div className="flex gap-2">
              <button
                id={`suite-run-btn-${s.id}`}
                disabled={runningId === s.id}
                onClick={() => handleRunSuite(s)}
                className="bg-green-700 hover:bg-green-600 disabled:opacity-50 px-3 py-1.5 rounded text-sm"
              >
                {runningId === s.id ? 'Starting…' : 'Run'}
              </button>
              <button
                id={`suite-delete-btn-${s.id}`}
                onClick={() => handleDelete(s.id)}
                className="bg-red-800 hover:bg-red-700 px-3 py-1.5 rounded text-sm"
              >
                Delete
              </button>
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}
