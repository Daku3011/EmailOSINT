import type { Breach } from "../lib/api";
import { ShieldAlert, ShieldCheck } from "lucide-react";

interface BreachTableProps {
  breaches: Breach[];
}

export default function BreachTable({ breaches }: BreachTableProps) {
  if (breaches.length === 0) {
    return (
      <div className="card-glass" id="breach-panel">
        <div className="flex items-center gap-3">
          <div className="p-2 rounded-lg bg-green-500/10">
            <ShieldCheck className="h-5 w-5 text-green-500" />
          </div>
          <div>
            <span className="font-medium text-green-400">No breaches found</span>
            <p className="text-xs text-muted-foreground mt-0.5">
              This email was not found in any known data breaches
            </p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="card-glass" id="breach-panel">
      <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
        <div className="p-1.5 rounded-lg bg-red-500/10">
          <ShieldAlert className="h-5 w-5 text-red-400" />
        </div>
        <span className="text-red-400">
          Breaches ({breaches.length})
        </span>
      </h3>
      <div className="space-y-3">
        {breaches.map((breach, i) => (
          <div
            key={`${breach.name}-${i}`}
            className="p-3.5 rounded-lg bg-background/50 border border-red-500/10 hover:border-red-500/20 transition-colors"
          >
            <div className="flex justify-between items-start gap-2">
              <div>
                <div className="font-medium text-sm">{breach.name}</div>
                {breach.domain && (
                  <div className="text-xs text-muted-foreground mt-0.5">
                    {breach.domain}
                  </div>
                )}
              </div>
              {breach.date && (
                <span className="text-xs text-muted-foreground whitespace-nowrap bg-secondary px-2 py-0.5 rounded">
                  {breach.date}
                </span>
              )}
            </div>
            {breach.data_classes.length > 0 && (
              <div className="flex flex-wrap gap-1.5 mt-2.5">
                {breach.data_classes.map((dc, j) => (
                  <span
                    key={j}
                    className="px-2 py-0.5 rounded-md bg-red-500/10 text-red-400 text-xs border border-red-500/20"
                  >
                    {dc}
                  </span>
                ))}
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}
