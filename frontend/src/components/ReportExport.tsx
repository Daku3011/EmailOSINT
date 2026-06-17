import type { Report } from "../lib/api";
import { FileJson, FileText } from "lucide-react";

interface ReportExportProps {
  report: Report;
}

export default function ReportExport({ report }: ReportExportProps) {
  const downloadBlob = (content: string, type: string, ext: string) => {
    const blob = new Blob([content], { type });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    const safe = report.email.replace(/[^a-zA-Z0-9@._-]/g, "_");
    a.download = `osint-report-${safe}.${ext}`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  const exportJSON = () => {
    downloadBlob(JSON.stringify(report, null, 2), "application/json", "json");
  };

  const exportCSV = () => {
    const headers = ["email", "domain", "risk_score", "breaches", "social_profiles", "gravatar"];
    const esc = (v: string) => `"${v.replace(/"/g, '""')}"`;
    const row = [
      report.email,
      report.domain_info?.domain ?? "",
      report.risk_score.toString(),
      report.breaches.map((b) => b.name).join("; "),
      report.usernames.map((u) => `${u.platform}:${u.username}`).join("; "),
      report.gravatar?.exists ? "Yes" : "No",
    ];
    const csv = [headers.join(","), row.map(esc).join(",")].join("\n");
    downloadBlob(csv, "text/csv;charset=utf-8", "csv");
  };

  return (
    <div className="flex gap-2" id="export-controls">
      <button
        id="export-json"
        onClick={exportJSON}
        className="flex items-center gap-2 px-3.5 py-2 rounded-lg bg-secondary hover:bg-secondary/80 text-sm font-medium transition-all border border-border/50"
        aria-label="Export report as JSON"
      >
        <FileJson className="h-4 w-4 text-primary" />
        JSON
      </button>
      <button
        id="export-csv"
        onClick={exportCSV}
        className="flex items-center gap-2 px-3.5 py-2 rounded-lg bg-secondary hover:bg-secondary/80 text-sm font-medium transition-all border border-border/50"
        aria-label="Export report as CSV"
      >
        <FileText className="h-4 w-4 text-primary" />
        CSV
      </button>
    </div>
  );
}
