#!/usr/bin/env bash
# stamp-stats.sh — carry in stats.json the provenance only the publish step knows.
#
# The pipeline writes stats.json as pure artifact state, and provenance cannot be
# one of its fields: `sync` publishes without regenerating it, so a value copied
# there would lag the data it describes. The publish step therefore stamps two
# fields as it publishes a snapshot:
#
#   publishedAt  when this snapshot was published (UTC, ISO-8601) — the identity a
#                consumer compares against to tell two snapshots apart
#   upstream     the mirror tag the bundled dataset came from — what its hashes
#                join on (absent when no dataset rides along)
#
# Both subcommands drop the stamped fields first, so core(stamped) equals
# core(unstamped): publish-dist can still recognise a no-op run by comparing
# stats.json with the stamp off, and only a snapshot that really changed gets a
# fresh time.
#
# usage:
#   stamp-stats.sh core   <file>                              print canonical JSON, stamped fields off
#   stamp-stats.sh stamp  <file> <publishedAt> <upstreamRef>  rewrite <file> in place (empty ref drops upstream)

set -euo pipefail

STAMPED='del(.publishedAt, .upstream)'

case "${1:-}" in
  core)
    jq -cS "$STAMPED" "${2:?usage: stamp-stats.sh core <file>}"
    ;;
  stamp)
    file="${2:?usage: stamp-stats.sh stamp <file> <publishedAt> <upstreamRef>}"
    published_at="${3:?}"
    upstream_ref="${4:-}"
    [ -f "$file" ] || { echo "no stats.json to stamp at $file" >&2; exit 1; }
    tmp="$(mktemp)"
    jq -S --indent 2 --arg at "$published_at" --arg ref "$upstream_ref" \
      "$STAMPED + {publishedAt: \$at} + (if \$ref == \"\" then {} else {upstream: \$ref} end)" \
      "$file" >"$tmp"
    mv "$tmp" "$file"
    ;;
  *)
    echo "usage: stamp-stats.sh core <file> | stamp <file> <publishedAt> <upstreamRef>" >&2
    exit 2
    ;;
esac
