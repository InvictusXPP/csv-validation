export default function FileUpload({ file, loading, onFileChange, onAnalyze }) {
  return (
    <section className="panel upload-panel">
      <h2>Wybierz plik</h2>
      <p>Wybierz plik CSV, aby sprawdzić jego zawartość.</p>
      <div className="upload-controls">
        <input type="file" accept=".csv,text/csv" onChange={onFileChange} />
        <button onClick={onAnalyze} disabled={!file || loading}>
          {loading ? 'Analizuję…' : 'Analizuj plik'}
        </button>
      </div>
      {file && <p className="selected-file">Wybrany plik: {file.name}</p>}
    </section>
  )
}
