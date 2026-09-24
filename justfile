# Write the two angles about the skills: one domain.json and one description_zh.json per skill.
#
#   just                  build the first skill missing its domain label (`just --list` for more)
#   just limit=20         ... the next 20 skills still unlabelled, most installed first
#   just limit=0          ... every skill in the snapshot, with no cap
#   just limit=20 jobs=8  the same window, eight labels at a time
#   just dry=1 limit=2    offline smoke test: fake endpoint, real layout
#   just translate        the second angle: the next skills' descriptions translated into Chinese
#   just skill-zh         the third angle: the next skills' SKILL.md bodies translated into Chinese
#   just index            write output/skills.jsonl: the mirror's rows joined with both angles
#                         ... and output/README.md beside it, the same tree said as progress
#
# Everything lands under `output_dir`, in layers that do not overlap. `skills/` holds one
# directory per skill, each stripped to its SKILL.md - the source the angles read, nothing more;
# the rest of what a skill ships stays upstream, and installing means fetching the skill's own
# repository. `profiles/` is what this project writes
# about them - one domain.json, one description_zh.json and one skill_zh.md per skill.
# `upstream/` holds the mirror's own files the tree reads, its index above all.
# `skills.jsonl` at the root is the catalog: one row per
# skill, the mirror's fields plus the description read out of the skill itself, its Chinese
# translation, and the domain it was labelled with. Publishing is copying that one directory.
#
# Two producers: `jev.py` asks the System One endpoint for the typed domain; `translate.py` asks
# an OpenAI-compatible chat endpoint for the Chinese description. The knobs are justfile
# variables: set on the command line and nowhere else. `.env` belongs to the scripts and holds the
# endpoints and their keys.

limit := "1"         # skills per run, most installed first: the next ones that need work; 0 = all
jobs := "32"         # calls in flight at once
dry := ""            # 1 = fake endpoint, real layout
output_dir := "output"
prompts_dir := "prompts"
snapshot := "https://codeload.github.com/skill-one/skills-sh-mirror/tar.gz/dist"
py := "uv run python"

# What the scripts read. Their configuration is the environment, so this is the handover.
export SKILLS_PROFILES_OUTPUT_DIR := output_dir
export SKILLS_PROFILES_PROMPTS_DIR := prompts_dir
export SKILLS_PROFILES_DRY_RUN := dry

# Build the missing domain labels for the next `limit` skills, most installed first.
default: (build "domain")

# Build the missing Chinese descriptions for the next `limit` skills, same window and pool.
translate: (build "description_zh")

# Build the missing Chinese SKILL.md pages for the next `limit` skills, same window and pool.
skill-zh: (build "skill_zh")

# The shared batch, for one angle: the next `limit` skills still missing that angle's file, most
# installed first, `jobs` at a time. `domain` is jev.py/domain.json; `description_zh` is
# translate.py/description_zh.json; `skill_zh` is skill_zh.py/skill_zh.md.
[script]
[private]
build angle:
	#!/usr/bin/env sh
	set -eu

	case "{{angle}}" in
		domain) script=jev.py; out=domain.json; label=domain ;;
		description_zh) script=translate.py; out=description_zh.json; label=translation ;;
		skill_zh) script=skill_zh.py; out=skill_zh.md; label="skill page" ;;
		*) echo "unknown angle: {{angle}}" >&2; exit 2 ;;
	esac
	export SCRIPT=$script
	export ANGLE_LABEL=$label

	# The order the run works in: the catalog's own, which is the mirror's.
	#
	# `skills.jsonl` is written with the mirror's rows in the mirror's order, so reading it is the
	# whole ordering - the most installed skills come first, and nothing is sorted. A row whose
	# description is `null` is a skill nothing could be read from, and neither batch touches it.
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

	# The window: the next `limit` skills still missing this angle's file, in that order. `0` = all.
	#
	# `limit` counts work rather than positions: a finished skill is not in the window, so repeated
	# runs walk down the dataset one window at a time. "not there yet" is one awk over two streams:
	# the skill dirs the tree already holds for this angle, then the order.
	present=$(find {{output_dir}}/profiles -mindepth 4 -maxdepth 4 -name "$out" 2>/dev/null \
		| sed "s|^{{output_dir}}/profiles/||; s|/$out\$||")
	skills=$( { printf '%s\n' "$present"; printf '%s\n' ---; printf '%s\n' "$ordered"; } \
		| awk -v limit={{limit}} '
			$0 == "---" { listing = 1; next }
			!listing { have[$0] = 1; next }
			!($0 in have) { print; taken++; if (limit && taken >= limit) exit }')
	[ -n "$skills" ] || { echo "nothing to build: every skill already has its $out" >&2; exit 0; }

	# A failed call must not end the run: the skill is named in FAIL_LOG so the next run redoes
	# exactly it, while the batch returns success so CI can publish the outputs that did build.
	# GEN_ERR_LOG receives the failing call's detail when CI provides it; otherwise it goes to
	# /dev/null. `-r` keeps an empty list from running the pool.
	printf '%s\n' "$skills" | xargs -r -P {{jobs}} -n 1 sh -c '
		err=$(mktemp)
		if {{py}} "$SCRIPT" "$1" 2>"$err"; then
			cat "$err" >&2
		else
			cat "$err" >>"${GEN_ERR_LOG:-/dev/null}"
			printf "FAILED %s %s\n" "$ANGLE_LABEL" "$1" >>"${FAIL_LOG:-/dev/null}"
			echo "failed: $1" >&2
		fi
		rm -f "$err"
		:' _

# Build exactly one domain label, whether or not the batch has reached it yet.
one skill:
	@{{py}} jev.py {{skill}}

# Translate exactly one skill's description, whether or not the batch has reached it yet.
translate-one skill:
	@{{py}} translate.py {{skill}}

# Translate exactly one skill's SKILL.md body, whether or not the batch has reached it yet.
skill-zh-one skill:
	@{{py}} skill_zh.py {{skill}}

# Print the request one label would send, calling nothing.
render skill:
	@{{py}} jev.py {{skill}} --print

# Print the request one translation would send, calling nothing.
translate-render skill:
	@{{py}} translate.py {{skill}} --print

# Forget every domain label, so the next run rebuilds them.
invalidate:
	@find {{output_dir}}/profiles -type f -name 'domain.json' -delete 2>/dev/null || true
	@echo "forgot every domain output"

# Forget every Chinese description, so the next translate run rebuilds them.
invalidate-translate:
	@find {{output_dir}}/profiles -type f -name 'description_zh.json' -delete 2>/dev/null || true
	@echo "forgot every translation output"

# Forget every Chinese SKILL.md page, so the next skill-zh run rebuilds them.
invalidate-skill-zh:
	@find {{output_dir}}/profiles -type f -name 'skill_zh.md' -delete 2>/dev/null || true
	@echo "forgot every Chinese skill page"

# Write the catalog and its READMEs: the mirror's rows joined with each skill's description, its
# Chinese translation and its domain, plus the front page of the published root - the same tree
# said as progress.
index:
	@{{py}} index.py

# The catalog `refresh` is about to replace: scratch, because `sync` rewrites that whole file.
[private]
capture-index:
	@cp "{{output_dir}}/skills.jsonl" ".previous-index" 2>/dev/null || rm -f .previous-index

# Re-fetch the snapshot and retire the angles whose source changed under them (DEVELOPING.md).
refresh: capture-index sync
	@{{py}} stale.py .previous-index; status=$?; rm -f .previous-index; exit $status

# Download the upstream snapshot and unpack it into the two layers the rest reads: one directory
# per skill, each stripped to its SKILL.md, and the mirror's own metadata - its index above all -
# beside them.
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
	# Space over fidelity: everything a skill ships but its SKILL.md is dropped here, empty
	# directories and all. A skill whose extras matter has them in its own repository.
	find "{{output_dir}}/skills.new" -type f ! -name SKILL.md -delete
	find "{{output_dir}}/skills.new" -type d -empty -delete
	mkdir -p "{{output_dir}}/upstream.new"
	find "$stage" -mindepth 1 -maxdepth 1 -exec mv {} "{{output_dir}}/upstream.new/" \;
	# The same reading for the mirror's own files: the tree reads its index, the version pointer
	# and the scan stats, so those three are all that survive.
	find "{{output_dir}}/upstream.new" -mindepth 1 -maxdepth 1 \
		! -name skills.jsonl ! -name latest ! -name stats.json -exec rm -rf {} +
	rm -rf "{{output_dir}}/skills" "{{output_dir}}/upstream"
	mv "{{output_dir}}/skills.new" "{{output_dir}}/skills"
	mv "{{output_dir}}/upstream.new" "{{output_dir}}/upstream"
	{{py}} index.py

# Drop the profiles, the catalog and the READMEs about them. The sources stay: they are what both
# angles are built from, and re-fetching them is the expensive part.
clean:
	@rm -rf {{output_dir}}/profiles {{output_dir}}/skills.jsonl \
		{{output_dir}}/README.md {{output_dir}}/README.zh-CN.md

# Run the tests: offline, with a fake endpoint and a local snapshot.
test:
	@uv run pytest
