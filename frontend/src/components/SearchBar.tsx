import { useState } from "react";
import { Search, Loader2 } from "lucide-react";

interface SearchBarProps {
  onSearch: (email: string) => void;
  loading: boolean;
}

export default function SearchBar({ onSearch, loading }: SearchBarProps) {
  const [email, setEmail] = useState("");

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    const trimmed = email.trim();
    if (trimmed && !loading) {
      onSearch(trimmed);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="w-full max-w-2xl mx-auto" role="search">
      <label htmlFor="email-input" className="sr-only">Email address</label>
      <div className="relative flex items-center">
        <input
          id="email-input"
          type="email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          placeholder="Enter email address to analyze..."
          className="w-full px-4 py-3.5 pl-12 rounded-xl bg-secondary/80 border border-border text-foreground placeholder-muted-foreground focus:outline-none focus:ring-2 focus:ring-ring focus:border-transparent transition-all"
          disabled={loading}
          autoComplete="email"
          aria-label="Email address to analyze"
        />
        <Search className="absolute left-4 h-5 w-5 text-muted-foreground" />
        <button
          id="analyze-button"
          type="submit"
          disabled={loading || !email.trim()}
          className="absolute right-2 px-5 py-2 rounded-lg bg-primary text-primary-foreground font-semibold text-sm hover:brightness-110 active:scale-[0.98] disabled:opacity-40 disabled:cursor-not-allowed transition-all"
        >
          {loading ? <Loader2 className="h-5 w-5 animate-spin" /> : "Analyze"}
        </button>
      </div>
    </form>
  );
}
