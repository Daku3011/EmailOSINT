import type { DomainInfo } from "../lib/api";
import { Globe, Server, Network, FileSearch } from "lucide-react";

interface DomainPanelProps {
  domain: DomainInfo;
}

export default function DomainPanel({ domain }: DomainPanelProps) {
  return (
    <div className="card-glass" id="domain-panel">
      <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
        <Globe className="h-5 w-5 text-primary" />
        Domain: {domain.domain}
      </h3>
      <div className="space-y-4">
        <div>
          <div className="flex items-center gap-2 text-sm text-muted-foreground mb-2">
            <Server className="h-4 w-4" /> MX Records
          </div>
          <div className="flex flex-wrap gap-1.5">
            {domain.mx_records.length > 0 ? (
              domain.mx_records.map((mx, i) => (
                <span
                  key={i}
                  className="px-2.5 py-1 rounded-md bg-secondary text-xs font-mono border border-border/50"
                >
                  {mx}
                </span>
              ))
            ) : (
              <span className="text-xs text-muted-foreground italic">
                No MX records found
              </span>
            )}
          </div>
        </div>

        <div>
          <div className="flex items-center gap-2 text-sm text-muted-foreground mb-2">
            <Network className="h-4 w-4" /> A Records
          </div>
          <div className="flex flex-wrap gap-1.5">
            {domain.dns_a_records.length > 0 ? (
              domain.dns_a_records.map((a, i) => (
                <span
                  key={i}
                  className="px-2.5 py-1 rounded-md bg-secondary text-xs font-mono border border-border/50"
                >
                  {a}
                </span>
              ))
            ) : (
              <span className="text-xs text-muted-foreground italic">
                No A records found
              </span>
            )}
          </div>
        </div>

        {domain.whois && (
          <div>
            <div className="flex items-center gap-2 text-sm text-muted-foreground mb-2">
              <FileSearch className="h-4 w-4" /> WHOIS Data
            </div>
            <pre className="text-xs font-mono text-muted-foreground p-3 rounded-lg bg-background/50 border border-border/30 max-h-32 overflow-y-auto whitespace-pre-wrap break-all">
              {JSON.stringify(domain.whois, null, 2).slice(0, 500)}
            </pre>
          </div>
        )}
      </div>
    </div>
  );
}
