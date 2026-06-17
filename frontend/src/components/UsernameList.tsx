import type { UsernameResult } from "../lib/api";
import { AtSign, ExternalLink, UserX } from "lucide-react";

interface UsernameListProps {
  usernames: UsernameResult[];
}

export default function UsernameList({ usernames }: UsernameListProps) {
  if (usernames.length === 0) {
    return (
      <div className="card-glass" id="social-panel">
        <div className="flex items-center gap-3">
          <div className="p-2 rounded-lg bg-muted">
            <UserX className="h-5 w-5 text-muted-foreground" />
          </div>
          <div>
            <span className="font-medium text-muted-foreground">
              No social profiles found
            </span>
            <p className="text-xs text-muted-foreground/70 mt-0.5">
              No matching profiles were discovered on major platforms
            </p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="card-glass" id="social-panel">
      <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
        <AtSign className="h-5 w-5 text-primary" />
        Social Profiles ({usernames.length})
      </h3>
      <div className="space-y-1">
        {usernames.map((u, i) => (
          <div
            key={`${u.platform}-${u.username}-${i}`}
            className="flex items-center justify-between py-2 px-3 rounded-lg hover:bg-secondary/60 transition-colors group"
          >
            <div className="flex items-center gap-2.5">
              <span className="text-sm font-medium">{u.platform}</span>
              <span className="text-xs text-muted-foreground font-mono">
                @{u.username}
              </span>
            </div>
            {u.profile_url && (
              <a
                href={u.profile_url}
                target="_blank"
                rel="noopener noreferrer"
                className="flex items-center gap-1 text-xs text-primary opacity-60 group-hover:opacity-100 hover:underline transition-opacity"
                aria-label={`Visit ${u.username} on ${u.platform}`}
              >
                Visit
                <ExternalLink className="h-3 w-3" />
              </a>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}
