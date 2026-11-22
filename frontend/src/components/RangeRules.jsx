export default function RangeRules({ rules, onChange }) {
  function updateRule(index, field, value) {
    onChange(rules.map((rule, ruleIndex) => ruleIndex === index ? { ...rule, [field]: value } : rule))
  }

  function addRule() {
    onChange([...rules, { column: '', min: '', max: '' }])
  }

  function removeRule(index) {
    onChange(rules.filter((_, ruleIndex) => ruleIndex !== index))
  }

  return (
    <section className="panel rules-panel">
      <div className="section-title">
        <div>
          <h2>Zakresy wartości liczbowych</h2>
          <p>Podaj nazwę kolumny i dozwolone minimum lub maksimum.</p>
        </div>
        <button className="secondary" type="button" onClick={addRule}>Dodaj zakres</button>
      </div>
      {rules.length === 0 ? <p className="muted">Nie dodano żadnych zakresów.</p> : rules.map((rule, index) => (
        <div className="rule-row" key={index}>
          <label>Kolumna
            <input value={rule.column} onChange={event => updateRule(index, 'column', event.target.value)} placeholder="np. age" />
          </label>
          <label>Minimum
            <input type="number" value={rule.min} onChange={event => updateRule(index, 'min', event.target.value)} placeholder="brak" />
          </label>
          <label>Maksimum
            <input type="number" value={rule.max} onChange={event => updateRule(index, 'max', event.target.value)} placeholder="brak" />
          </label>
          <button className="remove-rule" type="button" onClick={() => removeRule(index)} aria-label="Usuń zakres">Usuń</button>
        </div>
      ))}
      <p className="muted rules-note">Wpisz nazwę kolumny dokładnie tak, jak w nagłówku CSV. Puste limity nie będą sprawdzane.</p>
    </section>
  )
}
