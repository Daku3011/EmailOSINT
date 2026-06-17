import { useState } from "react";
import SearchBar from "./components/SearchBar";
import DomainPanel from "./components/DomainPanel";
import BreachTable from "./components/BreachTable";
import GravatarCard from "./components/GravatarCard";
import UsernameList from "./components/UsernameList";
import SearchResults from "./components/SearchResults";
import ReportExport from "./components/ReportExport";
import RiskChart from "./charts/RiskChart";
import { analyzeEmail, type Report } from "./lib/api";
import { AlertCircle, Mail, Shield, Sparkles } from "lucide-react";

export default function App() {
  const [report, setReport] = useState<Report | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSearch = async (email: string) => {
    setLoading(true);
    setError(null);
    setReport(null);
    try {
      const result = await analyzeEmail(email);
      setReport(result);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Analysis failed");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-background">
      <header className="border-b border-border/50 backdrop-blur-sm sticky top-0 z-50 bg-background/80">
        <div className="max-w-6xl mx-auto px-6 py-5">
          <div className="flex items-center gap-3 mb-5">
            <div className="p-2 rounded-lg bg-primary/10 border border-primary/20">
              <Shield className="h-7 w-7 text-primary" />
            </div>
            <div>
              <h1 className="text-2xl font-bold tracking-tight">Email OSINT</h1>
              <p className="text-sm text-muted-foreground">
                Open-source intelligence for email analysis
              </p>
            </div>
          </div>
          <SearchBar onSearch={handleSearch} loading={loading} />
        </div>
      </header>

      <main className="max-w-6xl mx-auto px-6 py-8">
        {loading && (
          <div className="flex flex-col items-center justify-center py-24 gap-4">
            <div className="relative">
              <div className="animate-spin rounded-full h-10 w-10 border-2 border-primary/20 border-t-primary"></div>
              <Sparkles className="absolute inset-0 m-auto h-4 w-4 text-primary animate-pulse" />
            </div>
            <span className="text-muted-foreground text-sm">
              Gathering intelligence across multiple sources...
            </span>
          </div>
        )}

        {error && (
          <div
            id="error-alert"
            className="flex items-center gap-3 p-4 rounded-lg bg-destructive/10 border border-destructive/30 text-red-400"
            role="alert"
          >
            <AlertCircle className="h-5 w-5 flex-shrink-0" />
            <span>{error}</span>
          </div>
        )}

        {report && (
          <div className="space-y-6 animate-in fade-in duration-500">
            <div className="flex items-center justify-between flex-wrap gap-3">
              <div className="flex items-center gap-2 text-sm text-muted-foreground">
                <Mail className="h-4 w-4" />
                <span className="font-medium text-foreground">{report.email}</span>
                <span className="px-2 py-0.5 rounded-md bg-primary/15 text-primary text-xs font-mono">
                  {report.id.slice(0, 8)}
                </span>
              </div>
              <ReportExport report={report} />
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
              <div className="lg:col-span-2 space-y-6">
                {report.domain_info && <DomainPanel domain={report.domain_info} />}
                <BreachTable breaches={report.breaches} />
                <UsernameList usernames={report.usernames} />
                <SearchResults results={report.search_results} />
              </div>
              <div className="space-y-6">
                <RiskChart
                  breachCount={report.breaches.length}
                  profileCount={report.usernames.length}
                  hasGravatar={report.gravatar?.exists ?? false}
                  riskScore={report.risk_score}
                />
                {report.gravatar && <GravatarCard gravatar={report.gravatar} />}
              </div>
            </div>
          </div>
        )}

        {!report && !loading && !error && (
          <div className="text-center py-24 text-muted-foreground">
            <div className="p-4 rounded-2xl bg-primary/5 border border-primary/10 inline-block mb-6">
              <Shield className="h-14 w-14 opacity-60" />
            </div>
            <p className="text-xl font-medium text-foreground mb-2">
              Enter an email to begin analysis
            </p>
            <p className="text-sm max-w-md mx-auto">
              Results include domain info, breach history, social profiles,
              web mentions, and a composite risk score
            </p>
          </div>
        )}
      </main>

      <footer className="border-t border-border/30 mt-12">
        <div className="max-w-6xl mx-auto px-6 py-4 text-center text-xs text-muted-foreground">
          Email OSINT v1.1 — For authorized security research only
        </div>
      </footer>
    </div>
  );
}
