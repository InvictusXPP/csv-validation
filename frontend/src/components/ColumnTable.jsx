export default function ColumnTable({ columns }) {
  return (
    <section className="panel">
      <h2>Kolumny</h2>
      <div className="table-scroll">
        <table>
          <thead><tr><th>Nazwa</th><th>Rozpoznany typ</th><th>Unikalne wartości</th><th>Puste</th><th>Przykłady</th></tr></thead>
          <tbody>{columns.map(column => <tr key={column.name}>
            <td>{column.name}</td><td>{column.detected_type}</td><td>{column.unique}</td><td>{column.missing}</td><td>{column.sample.join(', ') || '—'}</td>
          </tr>)}</tbody>
        </table>
      </div>
    </section>
  )
}
