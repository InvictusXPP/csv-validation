import ColumnTable from './ColumnTable.jsx'
import DataPreview from './DataPreview.jsx'
import IssuesTable from './IssuesTable.jsx'
import Summary from './Summary.jsx'

export default function ReportView({ report, onDownload }) {
  return <>
    <Summary report={report} onDownload={onDownload} />
    <ColumnTable columns={report.column_stats} />
    <IssuesTable issues={report.issues} />
    <DataPreview report={report} />
  </>
}
