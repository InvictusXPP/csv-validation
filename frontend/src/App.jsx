import { useState } from 'react'
import { analyzeCsv, downloadJsonReport } from './api.js'
import FileUpload from './components/FileUpload.jsx'
import RangeRules from './components/RangeRules.jsx'
import ReportView from './components/ReportView.jsx'

export default function App() {
  const [file, setFile] = useState(null)
  const [report, setReport] = useState(null)
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)
  const [rangeRules, setRangeRules] = useState([])

  function handleFileChange(event) {
    setFile(event.target.files?.[0] || null)
    setReport(null)
    setError('')
  }

  async function handleAnalyze() {
    if (!file) return
    const invalidRange = rangeRules.find(rule => rule.min !== '' && rule.max !== '' && Number(rule.min) > Number(rule.max))
    if (invalidRange) {
      setError(`Minimum nie może być większe niż maksimum dla kolumny „${invalidRange.column || 'bez nazwy'}”.`)
      return
    }
    const configuredRules = rangeRules
      .filter(rule => rule.column.trim() && (rule.min !== '' || rule.max !== ''))
      .reduce((result, rule) => {
        result[rule.column.trim()] = {
          type: 'number',
          ...(rule.min !== '' ? { min: Number(rule.min) } : {}),
          ...(rule.max !== '' ? { max: Number(rule.max) } : {}),
        }
        return result
      }, {})
    setLoading(true)
    setError('')
    setReport(null)
    try {
      setReport(await analyzeCsv(file, { columns: configuredRules }))
    } catch (analysisError) {
      setError(analysisError.message || 'Nie można połączyć się z serwerem.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <main className="page">
      <header className="header">
        <h1>DataCheck</h1>
        <p>Proste sprawdzanie jakości plików CSV</p>
      </header>

      <FileUpload file={file} loading={loading} onFileChange={handleFileChange} onAnalyze={handleAnalyze} />
      <RangeRules rules={rangeRules} onChange={setRangeRules} />
      {error && <p className="error">{error}</p>}
      {report && <ReportView report={report} onDownload={() => downloadJsonReport(report)} />}

      <footer>DataCheck · lokalna analiza plików CSV</footer>
    </main>
  )
}
