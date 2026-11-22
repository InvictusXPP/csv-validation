export default function IssuesTable({ issues }) {
  return (
    <section className="panel">
      <h2>Wykryte problemy <span className="muted">({issues.length})</span></h2>
      {issues.length ? <div className="table-scroll">
        <table>
          <thead><tr><th>Wiersz</th><th>Kolumna</th><th>Opis</th><th>Poziom</th><th>Wartość</th></tr></thead>
          <tbody>{issues.map((issue, index) => <tr key={`${issue.type}-${issue.row}-${index}`}>
            <td>{issue.row ?? '—'}</td><td>{issue.column ?? '—'}</td><td>{issue.message}</td><td>{issue.severity}</td><td>{issue.value ?? '—'}</td>
          </tr>)}</tbody>
        </table>
      </div> : <p>Nie znaleziono problemów.</p>}
    </section>
  )
}
