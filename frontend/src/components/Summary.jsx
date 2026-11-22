export default function Summary({ report, onDownload }) {
  const metrics = [
    ['Wynik jakości', `${report.score}/100`],
    ['Wiersze', report.rows],
    ['Kolumny', report.columns],
    ['Problemy', report.summary.issues],
    ['Puste komórki', report.summary.missing_cells],
    ['Duplikaty', report.summary.duplicates],
  ]

  return (
    <section className="panel">
      <div className="section-title">
        <div>
          <h2>Podsumowanie</h2>
          <p>Plik: {report.filename} · separator: {report.delimiter}</p>
        </div>
        <button className="secondary" onClick={onDownload}>Pobierz raport</button>
      </div>
      <div className="summary-grid">
        {metrics.map(([label, value]) => <div key={label}><span>{label}</span><strong>{value}</strong></div>)}
      </div>
    </section>
  )
}
