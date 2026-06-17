export interface DomainInfo {
  domain: string;
  mx_records: string[];
  dns_a_records: string[];
  whois: Record<string, unknown> | null;
}

export interface Breach {
  name: string;
  domain: string;
  date: string | null;
  data_classes: string[];
  description: string | null;
}

export interface GravatarResult {
  exists: boolean;
  avatar_url: string | null;
  profile_url: string | null;
}

export interface UsernameResult {
  username: string;
  platform: string;
  profile_url: string | null;
  exists: boolean;
}

export interface SearchResult {
  title: string;
  url: string;
  snippet: string | null;
}

export interface Report {
  id: string;
  email: string;
  is_valid: boolean;
  domain_info: DomainInfo | null;
  breaches: Breach[];
  gravatar: GravatarResult | null;
  usernames: UsernameResult[];
  search_results: SearchResult[];
  risk_score: number;
}

const API_BASE = "/api";

export async function analyzeEmail(email: string): Promise<Report> {
  const res = await fetch(`${API_BASE}/analyze`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email }),
  });
  if (!res.ok) {
    const err = await res.json();
    throw new Error(err.detail || "Analysis failed");
  }
  return res.json();
}

export async function getReport(id: string): Promise<Report> {
  const res = await fetch(`${API_BASE}/report/${id}`);
  if (!res.ok) throw new Error("Report not found");
  return res.json();
}
