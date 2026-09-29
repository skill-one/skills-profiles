# Build the two angles about the skills, or clean the same window back out:
#
#   just                       build the first skill missing its domain label (a one-skill smoke)
#   just build domain          ... the same thing, named
#   just build skill_zh        the second angle: the next skills' Chinese pages built
#   just limit=20 build domain the next 20 skills still unlabelled, most installed first
#   just limit=0 build domain  every skill in the snapshot, no cap
#   just limit=20 jobs=8 build domain   the same window, eight at a time
#   just dry=1 limit=2 build domain     fake the endpoints, real layout
#   just clean domain          the inverse: forget the first built skill's label
#   just limit=0 clean all     forget every built output of both angles
#   just sync                  reconcile with the mirror: listing, new sources, reindex
#   just index                 write output/skills.jsonl and the READMEs from what is on disk
#
# The orchestration is `batch.py`: it walks the catalog, fetches each window's repository once,
# and runs the producers in one in-process pool. This file only chooses which command runs with
# which knobs; `.env` belongs to the scripts and holds the endpoints and their keys.

limit := "1"         # skills per run, most installed first: the next ones that need work; 0 = all
jobs := "32"         # calls in flight at once
fetch_jobs := "16"   # repository tarballs in flight at once
dry := ""            # 1 = fake endpoint, real layout
output_dir := "output"
prompts_dir := "prompts"
# the mirror's listing, pulled fresh by `refresh` and never kept - the catalog is its lasting trace
listing := "https://raw.githubusercontent.com/skill-one/skills-sh-mirror/dist/skills.jsonl"
# where a repository's tarball comes from: {owner} and {repo} are substituted per repository
repo_tarball := "https://codeload.github.com/{owner}/{repo}/tar.gz/HEAD"
py := "uv run python"

# What the scripts read. Their configuration is the environment, so this is the handover.
export SKILLS_PROFILES_OUTPUT_DIR := output_dir
export SKILLS_PROFILES_PROMPTS_DIR := prompts_dir
export SKILLS_PROFILES_DRY_RUN := dry

# A bare `just` is the one-skill smoke: one domain label, most installed first.
default: (build "domain")

# Build the missing outputs of one angle for the next `limit` skills, most installed first.
build angle:
	@{{py}} batch.py build {{ if angle == "domain" { angle } else if angle == "skill_zh" { angle } else { error("angle must be 'domain' or 'skill_zh'") } }} \
		--limit {{limit}} --jobs {{jobs}} --fetch-jobs {{fetch_jobs}} \
		--repo-tarball "{{repo_tarball}}"

# The inverse of build: delete the same angle's outputs from the first `limit` *built* skills
# (0 = every one; `all` = both angles' files). A bad angle fails before any command runs.
clean angle:
	@{{py}} batch.py clean {{ if angle == "domain" { angle } else if angle == "skill_zh" { angle } else if angle == "all" { angle } else { error("angle must be 'domain', 'skill_zh' or 'all'") } }} --limit {{limit}}

# Write the catalog and its READMEs: the mirror's rows joined with each skill's description, its
# Chinese translation and its domain, plus the front page of the published root.
index:
	@{{py}} index.py

# Reconcile with the mirror: pull its listing, refetch repositories it adds a skill to, reindex.
sync:
	@{{py}} batch.py sync --listing "{{listing}}" --fetch-jobs {{fetch_jobs}} \
		--repo-tarball "{{repo_tarball}}"

# Run the tests: offline, with a fake endpoint and a local snapshot.
test:
	@uv run pytest
