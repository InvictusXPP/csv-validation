const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

export async function analyzeCsv(file, rules = {}) {
  const form = new FormData()
  form.append('file', file)
  form.append('rules', JSON.stringify(rules))
  const response = await fetch(`${API_URL}/api/analyze`, { method: 'POST', body: form })
  const result = await response.json()
  if (!response.ok) throw new Error(result.detail || 'Wystąpił błąd podczas analizy pliku.')
  return result
}

export function downloadJsonReport(report) {
  const blob = new Blob([JSON.stringify(report, null, 2)], { type: 'application/json' })
  const url = URL.createObjectURL(blob)
  const link = document.createElement('a')
  link.href = url
  link.download = `${report.filename.replace(/\.csv$/i, '')}-raport.json`
  link.click()
  URL.revokeObjectURL(url)
}
