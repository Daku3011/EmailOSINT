import type { GravatarResult } from "../lib/api";
import { UserCircle, ExternalLink } from "lucide-react";

interface GravatarCardProps {
  gravatar: GravatarResult;
}

export default function GravatarCard({ gravatar }: GravatarCardProps) {
  return (
    <div className="card-glass" id="gravatar-panel">
      <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
        <UserCircle className="h-5 w-5 text-primary" />
        Gravatar
      </h3>
      <div className="flex items-center gap-4">
        {gravatar.exists && gravatar.avatar_url ? (
          <img
            src={gravatar.avatar_url}
            alt="Gravatar profile picture"
            className="w-16 h-16 rounded-full border-2 border-primary/40 ring-2 ring-primary/10"
            loading="lazy"
          />
        ) : (
          <div className="w-16 h-16 rounded-full bg-secondary flex items-center justify-center border border-border">
            <UserCircle className="h-8 w-8 text-muted-foreground" />
          </div>
        )}
        <div>
          <div className="font-medium">
            {gravatar.exists ? (
              <span className="text-green-400">Profile found</span>
            ) : (
              <span className="text-muted-foreground">No Gravatar found</span>
            )}
          </div>
          {gravatar.profile_url && (
            <a
              href={gravatar.profile_url}
              target="_blank"
              rel="noopener noreferrer"
              className="inline-flex items-center gap-1 text-sm text-primary hover:underline mt-1"
            >
              View profile
              <ExternalLink className="h-3 w-3" />
            </a>
          )}
        </div>
      </div>
    </div>
  );
}
