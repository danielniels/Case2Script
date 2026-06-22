/**
 * Single gateway for all FE→BE communication.
 * Uses relative paths so the same code works in dev (Vite proxy → :8000)
 * and prod (FastAPI serves the dist/ directly).
 */

const BASE = ''  // always relative

async function _fetch(path, options = {}) {
  const res = await fetch(`${BASE}${path}`, {
    headers: { 'Content-Type': 'application/json', ...options.headers },
    ...options,
  })
  if (!res.ok) {
    const err = await res.json().catch(() => ({ error: res.statusText }))
    throw Object.assign(new Error(err.error || res.statusText), { status: res.status, data: err })
  }
  return res.json()
}

// ── Suites ──────────────────────────────────────────────────────────────────

export const suites = {
  list: () => _fetch('/suites'),
  get: (id) => _fetch(`/suites/${id}`),
  create: (body) => _fetch('/suites', { method: 'POST', body: JSON.stringify(body) }),
  update: (id, body) => _fetch(`/suites/${id}`, { method: 'PUT', body: JSON.stringify(body) }),
  delete: (id) => _fetch(`/suites/${id}`, { method: 'DELETE' }),
}

// ── Runs ─────────────────────────────────────────────────────────────────────

export const runs = {
  list: () => _fetch('/runs'),
  get: (id) => _fetch(`/runs/${id}`),
  start: (body) => _fetch('/runs', { method: 'POST', body: JSON.stringify(body) }),
  stop: (id) => _fetch(`/runs/${id}/stop`, { method: 'POST' }),
  /** Returns an EventSource connected to SSE stream */
  events: (id) => new EventSource(`/runs/${id}/events`),
}

// ── Converters ───────────────────────────────────────────────────────────────

export const converters = {
  fromJson: (body) => _fetch('/convert/json', { method: 'POST', body: JSON.stringify(body) }),
  fromPrompt: (text, name = '') =>
    _fetch('/convert/prompt', { method: 'POST', body: JSON.stringify({ text, name }) }),
  /** Upload Excel — uses FormData, no Content-Type override */
  fromExcel: async (file) => {
    const fd = new FormData()
    fd.append('file', file)
    const res = await fetch('/convert/excel', { method: 'POST', body: fd })
    if (!res.ok) throw new Error(await res.text())
    return res.json()
  },
  excelTemplate: () => '/convert/excel/template',
}

// ── Health ───────────────────────────────────────────────────────────────────

export const health = () => _fetch('/health')

// ── Helpers ──────────────────────────────────────────────────────────────────

/** Convert a backend screenshot_path (e.g. data/saved_screenshots/…/step_1.png) to a URL */
export function screenshotUrl(path) {
  if (!path) return null
  return '/' + path.replace(/\\/g, '/')
}

/** URL for downloading the generated Playwright .js script */
export function scriptDownloadUrl(path) {
  if (!path) return null
  return `/api/scripts/download?path=${encodeURIComponent(path)}`
}

/** URL for viewing/downloading the JSON test report */
export function reportViewUrl(path) {
  if (!path) return null
  return '/' + path.replace(/\\/g, '/')
}
