# Label the skills with their domain: one domain.json per skill.
#
#   just                  build the first skill missing its label (`just --list` for more)
#   just limit=20         ... the next 20 skills still unlabelled, most installed first
#   just limit=0          ... every skill in the snapshot, with no cap
#   just limit=20 jobs=8  the same window, eight labels at a time
#   just rpm=20           ... paced to 20 calls a minute, whatever the pool size
#   just dry=1 limit=2    offline smoke test: fake endpoint, real layout
#   just index            write output/skills.jsonl: the mirror's rows joined with the labels
#                         ... and output/README.md beside it, the same tree said as progress
#
# Everything lands under `output_dir`, in layers that do not overlap. `skills/` is the mirror's
# own skill directories, exactly as it publishes them. `profiles/` is what this project writes
# about them - one domain.json per skill. `upstream/` is the rest of the mirror, its own index
# above all. `skills.jsonl` at the root is the catalog: one row per skill, the mirror's fields plus
# the description read out of the skill itself and the domain it was labelled with. Publishing is
# copying that one directory.
#
# The one producer is `jev.py`, which asks the System One endpoint. The knobs are justfile
# variables: set on the command line and nowhere else. `.env` belongs to the script and holds the
# endpoint and its key.

limit := "1"         # skills per run, most installed first: the next ones that need work; 0 = all
jobs := num_cpus()   # labels in flight at once
rpm := "0"           # what the endpoint allows per minute; 0 = no pace
dry := ""            # 1 = fake endpoint, real layout
output_dir := "output"
prompts_dir := "prompts"
snapshot := "https://codeload.github.com/skill-one/skills-sh-mirror/tar.gz/dist"
py := "uv run python"

# What jev.py reads. Its configuration is the environment, so this is the handover.
export SKILLS_PROFILES_OUTPUT_DIR := output_dir
export SKILLS_PROFILES_PROMPTS_DIR := prompts_dir
export SKILLS_PROFILES_DRY_RUN := dry

# Build the missing labels for the next `limit` skills, most installed first, `jobs` at a time.
[script]
default:
	#!/usr/bin/env sh
	set -eu

	# The order the run works in: the catalog's own, which is the mirror's.
	#
	# `skills.jsonl` is written with the mirror's rows in the mirror's order, so reading it is the
	# whole ordering - the most installed skills come first, and nothing is sorted. A row whose
	# description is `null` is a skill nothing could be read from, and the batch never touches it.
	# An id it names whose SKILL.md is not on disk is skipped.
	#
	# No catalog, or one whose ids do not parse, falls back to the directory listing in path order:
	# a `find` rather than a glob (a glob drops a leading dot, and `.claude` is a repo name people
	# use) and `LC_ALL=C sort` rather than plain `sort`, whose collation moves `_` around.
	[ -d {{output_dir}}/skills ] || { echo "no sources under {{output_dir}} - run \`just sync\` first" >&2; exit 1; }
	ordered=
	if [ -f {{output_dir}}/skills.jsonl ]; then
		ordered=$(grep -v '"description":null' {{output_dir}}/skills.jsonl \
			| sed -En 's/^ *\{ *"id" *: *"([^"]*)".*/\1/p' \
			| tr ':&' '__' \
			| while read -r skill; do
				if [ -f {{output_dir}}/skills/"$skill"/SKILL.md ]; then echo "$skill"; fi
			done)
	fi
	[ -n "$ordered" ] || ordered=$(find {{output_dir}}/skills -mindepth 4 -maxdepth 4 -name SKILL.md \
		| sed 's|^{{output_dir}}/skills/||; s|/SKILL.md$||' | LC_ALL=C sort)
	[ -n "$ordered" ] || { echo "no skill under {{output_dir}}/skills has a SKILL.md" >&2; exit 1; }

	# The window: the next `limit` skills still missing domain.json, in that order. `0` = all.
	#
	# `limit` counts work rather than positions: a finished skill is not in the window, so repeated
	# runs walk down the dataset one window at a time. "not there yet" is one awk over two streams:
	# the labelled skill dirs the tree already holds, then the order.
	present=$(find {{output_dir}}/profiles -mindepth 4 -maxdepth 4 -name domain.json 2>/dev/null \
		| sed 's|^{{output_dir}}/profiles/||; s|/domain.json$||')
	skills=$( { printf '%s\n' "$present"; printf '%s\n' ---; printf '%s\n' "$ordered"; } \
		| awk -v limit={{limit}} '
			$0 == "---" { listing = 1; next }
			!listing { have[$0] = 1; next }
			!($0 in have) { print; taken++; if (limit && taken >= limit) exit }')
	[ -n "$skills" ] || { echo "nothing to build: every skill already has its domain label" >&2; exit 0; }

	# `rpm` is a pace rather than a queue: a worker waits that long between its calls, so a batch
	# cannot outrun the endpoint. The pool is capped at it too, so the first round fits.
	pool={{jobs}}
	interval=0
	if [ "{{rpm}}" -gt 0 ]; then
		[ "$pool" -le "{{rpm}}" ] || pool={{rpm}}
		interval=$(( pool * 60 / {{rpm}} ))
	fi
	export INTERVAL=$interval
	if [ "$interval" -gt 0 ]; then
		echo "pacing: $pool at a time, one call per ${interval}s per worker" >&2
	fi

	# A failed call must not end the run: the skill is named in FAIL_LOG so the next run redoes
	# exactly it, and the pace is paid either way. stderr progress goes through; only a failing
	# call's traceback is filed away in GEN_ERR_LOG. `-r` keeps an empty list from running the pool.
	printf '%s\n' "$skills" | xargs -r -P "$pool" -n 1 sh -c '
		err=$(mktemp)
		start=$(date +%s)
		if {{py}} jev.py "$1" 2>"$err"; then
			cat "$err" >&2
		else
			cat "$err" >>"${GEN_ERR_LOG:-/dev/null}"
			printf "FAILED domain %s\n" "$1" >>"${FAIL_LOG:-/dev/null}"
			echo "failed: $1" >&2
		fi
		rm -f "$err"
		# `interval` is a floor on the time between two calls, not a rest after one.
		pause=$(( INTERVAL - ($(date +%s) - start) ))
		[ "$pause" -gt 0 ] && sleep "$pause"
		:' _

# Build exactly one label, whether or not the batch has reached it yet.
one skill:
	@{{py}} jev.py {{skill}}

# Print the request one label would send, calling nothing.
render skill:
	@{{py}} jev.py {{skill}} --print

# Forget every domain label, so the next run rebuilds them.
invalidate:
	@find {{output_dir}}/profiles -type f -name 'domain.json' -delete 2>/dev/null || true
	@echo "forgot every domain output"

# Write the catalog and its READMEs: the mirror's rows joined with each skill's description and its
# domain, plus the front page of the published root - the same tree said as progress.
index:
	@{{py}} index.py

# The catalog `refresh` is about to replace: scratch, because `sync` rewrites that whole file.
[private]
capture-index:
	@cp "{{output_dir}}/skills.jsonl" ".previous-index" 2>/dev/null || rm -f .previous-index

# Re-fetch the snapshot and retire the labels whose source changed under them (DEVELOPING.md).
refresh: capture-index sync
	@{{py}} stale.py .previous-index; status=$?; rm -f .previous-index; exit $status

# Download the upstream snapshot and unpack it into the two layers the rest reads: the skill
# directories a user installs, and the mirror's own metadata - its index above all - beside them.
#
# The fetch lands in a scratch directory beside the output root and the swap happens only once it
# is whole, so a broken download changes nothing; the guard is what keeps `rm -rf` away from an
# `output_dir` that is not this tree's. The catalog is rewritten last, because a sync moves the
# source layer under it.
[script]
sync:
	#!/usr/bin/env sh
	set -eu

	stage={{output_dir}}.new
	trap 'rm -rf "$stage"' EXIT
	if [ -d "{{output_dir}}/skills" ] \
		&& [ -z "$(find "{{output_dir}}/skills" -mindepth 4 -maxdepth 4 -name SKILL.md -print -quit)" ]; then
		echo "{{output_dir}}/skills exists and is not a snapshot - point output_dir elsewhere" >&2
		exit 1
	fi
	rm -rf "$stage"
	mkdir -p "$stage"
	curl -fsSL --retry 3 {{snapshot}} -o "$stage/archive.tar.gz"
	tar xzf "$stage/archive.tar.gz" -C "$stage" --strip-components=1
	rm -f "$stage/archive.tar.gz"
	[ -d "$stage/skills" ] || { echo "not a snapshot: what was fetched has no skills/" >&2; exit 1; }

	mkdir -p "{{output_dir}}"
	rm -rf "{{output_dir}}/skills.new" "{{output_dir}}/upstream.new"
	mv "$stage/skills" "{{output_dir}}/skills.new"
	mkdir -p "{{output_dir}}/upstream.new"
	find "$stage" -mindepth 1 -maxdepth 1 -exec mv {} "{{output_dir}}/upstream.new/" \;
	rm -rf "{{output_dir}}/skills" "{{output_dir}}/upstream"
	mv "{{output_dir}}/skills.new" "{{output_dir}}/skills"
	mv "{{output_dir}}/upstream.new" "{{output_dir}}/upstream"
	{{py}} index.py

# Drop the labels, the catalog and the READMEs about them. The sources stay: they are what a label
# is built from, and re-fetching them is the expensive part.
clean:
	@rm -rf {{output_dir}}/profiles {{output_dir}}/skills.jsonl \
		{{output_dir}}/README.md {{output_dir}}/README.zh-CN.md

# Run the tests: offline, with a fake endpoint and a local snapshot.
test:
	@uv run pytest
