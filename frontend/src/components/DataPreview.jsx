export default function DataPreview({ report }) {
  const columns = report.column_stats
  return (
    <section className="panel">
      <h2>Podgląd danych</h2>
      <div className="table-scroll">
        <table>
          <thead><tr>{columns.map(column => <th key={column.name}>{column.name}</th>)}</tr></thead>
          <tbody>{report.preview.slice(0, 10).map((row, index) => <tr key={index}>
            {columns.map(column => <td key={column.name}>{row[column.name] ?? '—'}</td>)}
          </tr>)}</tbody>
        </table>
      </div>
      <p className="muted">Wyświetlono maksymalnie 10 z {report.rows} wierszy.</p>
    </section>
  )
}
