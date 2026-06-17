import type { SearchResult } from "../lib/api";
import { Search, ExternalLink } from "lucide-react";

interface SearchResultsProps {
  results: SearchResult[];
}

export default function SearchResults({ results }: SearchResultsProps) {
  if (results.length === 0) return null;

  return (
    <div className="card-glass" id="search-panel">
      <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
        <Search className="h-5 w-5 text-primary" />
        Web Mentions ({results.length})
      </h3>
      <div className="space-y-1.5 max-h-56 overflow-y-auto pr-1">
        {results.map((r, i) => (
          <a
            key={i}
            href={r.url}
            target="_blank"
            rel="noopener noreferrer"
            className="flex items-center gap-2 p-2.5 rounded-lg hover:bg-secondary/60 text-sm truncate group transition-colors"
          >
            <ExternalLink className="h-3.5 w-3.5 text-muted-foreground flex-shrink-0 group-hover:text-primary transition-colors" />
            <span className="text-primary truncate">{r.url}</span>
          </a>
        ))}
      </div>
    </div>
  );
}
