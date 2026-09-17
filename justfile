# Generate the skill profiles: one json + one markdown per (skill, prompt).
#
#   just                  build the first skill's missing outputs (`just --list` for more)
#   just limit=0          ... every skill in the snapshot, with no cap
#   just prompt=scenario  ... only that angle, for every skill in the window
#   just limit=20 jobs=8  ... the 20 most installed skills, eight generations at a time
#   just rpm=20           ... paced to 20 calls a minute, whatever the pool size
#   just dry=1 limit=2    offline smoke test: fake model, real layout
#   just index            write output/skills.jsonl from the domains built so far
#
# Everything lands under `output_dir`: the profiles, the index beside them, and the snapshot they
# were built from - so publishing is copying that one directory, sources included.
#
# The knobs are justfile variables: they are set on the command line and nowhere else. `.env`
# belongs to gen.py, and holds the endpoint and its key.

limit := "1"         # skills per run, most installed first; 0 = all, with no cap
prompt := ""         # one prompt id, or empty for every prompt
jobs := num_cpus()   # generations in flight at once
rpm := "0"           # what the endpoint allows per minute; 0 = no pace
dry := ""            # 1 = fake model, real layout
output_dir := "output"
data_dir := output_dir / "cache" / "skills-sh"  # inside the output root, and following it
prompts_dir := "prompts"
snapshot := "https://codeload.github.com/skill-one/skills-sh-mirror/tar.gz/dist"
py := "uv run python"

# What gen.py reads. Its configuration is the environment, so this is the handover - and it is
# also why the pool below runs gen.py rather than `just one`: a nested just would re-evaluate
# this file and reset every one of these to its default.
export SKILLS_PROFILES_DATA_DIR := data_dir
export SKILLS_PROFILES_OUTPUT_DIR := output_dir
export SKILLS_PROFILES_PROMPTS_DIR := prompts_dir
export SKILLS_PROFILES_DRY_RUN := dry

# Build the missing outputs for the first `limit` skills, most installed first, `jobs` at a time.
[script]
default:
	#!/usr/bin/env sh
	set -eu

	# The window: the skills this run may build, in the order it works them.
	#
	# The order is the snapshot's own. `skills.jsonl` is written installs-descending, so reading
	# it is the whole ordering - a bounded `limit` does the most installed skills first, and
	# nothing is sorted. An id it names whose SKILL.md is not on disk is skipped, because the
	# index and the tree are written separately and can disagree.
	#
	# No index, or one whose ids do not parse, falls back to the directory listing in path order,
	# so a batch runs either way. That walk is a `find` rather than a glob (a glob drops a leading
	# dot, and `.claude` is a repo name people use) and `LC_ALL=C sort` rather than plain `sort`,
	# whose collation moves `_` around: the window has to be the same one in every locale.
	[ -d {{data_dir}}/skills ] || { echo "no snapshot under {{data_dir}} - run \`just sync\` first" >&2; exit 1; }
	window() {
		ordered=
		if [ -f {{data_dir}}/skills.jsonl ]; then
			ordered=$(sed -En 's/^ *\{ *"id" *: *"([^"]*)".*/\1/p' {{data_dir}}/skills.jsonl \
				| tr ':&' '__' \
				| while read -r skill; do
					if [ -f {{data_dir}}/skills/"$skill"/SKILL.md ]; then echo "$skill"; fi
				done)
		fi
		[ -n "$ordered" ] || ordered=$(find {{data_dir}}/skills -mindepth 4 -maxdepth 4 -name SKILL.md \
			| sed 's|^{{data_dir}}/skills/||; s|/SKILL.md$||' | LC_ALL=C sort)
		printf '%s\n' "$ordered" | awk -v n={{limit}} 'NR <= n || ! n'
	}
	skills=$(window)
	[ -n "$skills" ] || { echo "no skill under {{data_dir}}/skills has a SKILL.md" >&2; exit 1; }
	prompts=$(find {{prompts_dir}} -maxdepth 1 -name '*.json' | sed 's|.*/||; s|\.json$||')
	[ -n "$prompts" ] || { echo "no prompt schemas under {{prompts_dir}}" >&2; exit 1; }
	if [ -n "{{prompt}}" ]; then
		one=$(printf '%s\n' $prompts | grep -x '{{prompt}}') || {
			echo "no prompt '{{prompt}}' - have: $prompts" >&2; exit 1; }
		prompts=$one
	fi

	# `rpm` is a pace rather than a queue: a worker waits that long between its calls, so a
	# batch cannot outrun the endpoint. The pool is capped at it too, so the first round fits.
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

	for prompt in $prompts; do
		printf '%s\n' "$skills" | while read -r skill; do
			json={{output_dir}}/skills/$(echo "$skill" | tr ':&' '__')/$prompt.json
			[ -f "$json" ] || echo "$prompt $skill"
		done
	# A failed call must not end the run: `xargs` stops on 255 and reports 123, and either
	# one throws away every hour left in a long batch. The pair is named in FAIL_LOG so the
	# next run redoes exactly it, and the pace is paid either way - a systemic outage would
	# otherwise spin through every remaining skill in minutes, all of them failing.
	#
	# stderr is held back rather than redirected wholesale, because that is where the
	# progress line goes; only a failing call's traceback is filed away, in GEN_ERR_LOG.
	# `-r` keeps an empty list from running the pool once with no pair at all.
	done | xargs -r -P "$pool" -n 2 sh -c '
		err=$(mktemp)
		start=$(date +%s)
		if {{py}} gen.py "$@" 2>"$err"; then
			cat "$err" >&2
		else
			cat "$err" >>"${GEN_ERR_LOG:-/dev/null}"
			printf "FAILED %s %s\n" "$1" "$2" >>"${FAIL_LOG:-/dev/null}"
			echo "failed: $2 $1" >&2
		fi
		rm -f "$err"
		# `interval` is a floor on the time between two calls, not a rest after one: a call
		# takes a good part of it, and sleeping the whole of it on top would spend the
		# budget on the network instead of on the endpoint - half the allowed rate, gone.
		pause=$(( INTERVAL - ($(date +%s) - start) ))
		[ "$pause" -gt 0 ] && sleep "$pause"
		:' _

# Build exactly one output, whether or not the batch has reached it yet.
one prompt skill:
	@{{py}} gen.py {{prompt}} {{skill}}

# Print the request one output would send, calling nothing.
render prompt skill:
	@{{py}} gen.py {{prompt}} {{skill}} --print

# Forget one prompt's outputs, so the next run rebuilds them.
invalidate prompt:
	@find {{output_dir}}/skills -type f \( -name '{{prompt}}.json' -o -name '{{prompt}}.md' \) -delete 2>/dev/null || true
	@echo "forgot every {{prompt}} output"

# Write the index: one flat line per skill that has a domain, read off the output tree.
index:
	@{{py}} index.py

# The index of the snapshot `refresh` is about to replace: scratch, because `sync` swaps the whole
# snapshot directory and nothing inside it survives to be compared against.
[private]
capture-index:
	@cp "{{data_dir}}/skills.jsonl" ".snapshot-index" 2>/dev/null || rm -f .snapshot-index

# Re-fetch the snapshot and retire the profiles whose source changed under them (DEVELOPING.md).
refresh: capture-index sync
	@{{py}} stale.py .snapshot-index; status=$?; rm -f .snapshot-index; exit $status

# Download the upstream snapshot, replacing what is in the data dir.
[script]
sync:
	#!/usr/bin/env sh
	set -eu

	data={{data_dir}}
	if [ -e "$data" ] && [ ! -d "$data/skills" ]; then
		echo "$data exists and is not a snapshot - point data_dir elsewhere" >&2
		exit 1
	fi
	rm -rf "$data.new" "$data.tar.gz"
	mkdir -p "$data.new"
	curl -fsSL --retry 3 {{snapshot}} -o "$data.tar.gz"
	tar xzf "$data.tar.gz" -C "$data.new" --strip-components=1
	rm -rf "$data"
	mv "$data.new" "$data"
	rm -f "$data.tar.gz"

# Drop the profiles. The snapshot in the same root stays: re-fetching it is the expensive part.
clean:
	@rm -rf {{output_dir}}/skills {{output_dir}}/skills.jsonl

# Run the tests: offline, with a fake model and a local snapshot.
test:
	@uv run pytest
