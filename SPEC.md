# skills-profiles: the outside

The black-box view: everything a user or a consumer can see, and nothing about how it is built.

**The product is one directory** — `output/`: a tree of Chinese profiles, six angles per skill, each
angle one LLM turn over that skill's `SKILL.md`, with the snapshot those profiles were built from
kept beside them. The generator exists to produce that directory, so it is the interface, and the
commands only decide which part of it gets written.

中文: [SPEC.zh-CN.md](SPEC.zh-CN.md)

## 1. Output — the interface


```
<output_dir>/
├── skills/<id>/
│   ├── domain.json  scenario.json  tagline.json
│   ├── blackbox.json  whitebox.json  comments.json
│   └── md/<angle>.md      # the same content, rendered for reading
├── skills.jsonl           # `just index`: the listing of that tree, one flat line per skill
└── cache/skills-sh/       # the upstream snapshot those profiles were built from
```

`<id>` is the skill id, `{owner}/{repo}/{slug}`, with `:` and `&` rewritten to `_`. It is the join
key with the upstream mirror and with `https://www.skills.sh/<id>`.

| angle | json shape | content |
| --- | --- | --- |
| `domain` | `{domain, reason}` | one of 13 closed categories, plus one line of why |
| `scenario` | `{text}` | a ≤100-character pitch, built on the user's pain point |
| `tagline` | `{taglines[3]}` | three slogans, ≤20 characters each |
| `blackbox` | `{function, input_output[3–5]}` | outside view: what you hand it → what you get back |
| `whitebox` | `{execution_flow[3–5], mechanisms[2–3]}` | inside view: happy path, mechanisms, real dependencies |
| `comments` | `{comments[4–6]}` | first-person user notes: `{user, category, comment}` |

- One directory per skill, one file per angle. Every angle is independent — no file reads another.
- A `.json` is the data; `md/<angle>.md` is the same fields rendered, written first.
- **The tree is the only contract.** `skills.jsonl` is a derived listing of it, written by
  `just index`: one flat line per skill — `{id, domain, reason}`, in path order, and no line at all
  for a skill whose domain is not built. Nothing reads it.
- Ids, paths and field names are ASCII; every value is Chinese. `domain.domain` is a closed enum,
  so it filters directly.

## 2. Input

| what | where | put there by |
| --- | --- | --- |
| the snapshot: `skills/<id>/SKILL.md` and the files beside it | `data_dir` — `output_dir/cache/skills-sh` by default, so it publishes with the profiles | `just sync`, from the upstream `dist` branch |
| a prompt: `prompts/<id>.md` (the task) + `prompts/<id>.json` (its schema) | `prompts_dir` | you, by hand |
| the shared system prompt `prompts/_system.md` | `prompts_dir` | you |

The snapshot's own `skills.jsonl` — a different file from the profile index at the output root — is
the one file of it a run reads besides the sources: it orders the window, installs descending.
Absent, or in another shape, the window falls back to the tree in path order.

The snapshot is a fetched mirror, read-only. A prompt is a task/contract pair: the schema travels
to the provider verbatim as a strict `json_schema` response format. **Adding an angle is two files
and no code.**

## 3. Control

The batch is one recipe with modifiers, plus six verbs:

| command | does |
| --- | --- |
| `just` | build every missing (skill, angle) in the window |
| `just one <angle> <id>` | build one cell, inside or outside the window |
| `just invalidate <angle>` | delete that angle's outputs, everywhere |
| `just index` | fold the built domains into `skills.jsonl` |
| `just sync` | fetch the snapshot, replacing it wholesale |
| `just refresh` | fetch it, and drop every profile whose source hash changed with it |
| `just clean` | drop the profiles — `skills/` and `skills.jsonl`; the snapshot stays |
| `just render <angle> <id>` · `just test` | dev only: print the request · run the suite |

The modifiers are command-line variables, nowhere else:

| knob | default | meaning |
| --- | --- | --- |
| `limit` | 1 | the first N skills in the snapshot's own order — installs, descending; `0` = all, with no cap |
| `prompt` | – | one angle, or every angle |
| `jobs` | one per core | generations in flight at once |
| `rpm` | 0 | pace the run to the endpoint's per-minute allowance |
| `dry` | – | `1` = fake model, real layout |
| `data_dir` `output_dir` `prompts_dir` `snapshot` `py` | see [DEVELOPING.md](DEVELOPING.md) | plumbing |

Under it, one cell at a time:

```
gen.py <angle> <id> [--print]
```

- stdout is data (the request, under `--print`); stderr is progress.
- The source is cut at 20 000 characters, and the cut is announced inside the source itself.
- Exit: `0` built · `1` unusable input or model · `2` bad arguments.

## 4. Configuration

`.env` (copy [`.env.example`](.env.example)) or `SKILLS_PROFILES_*`; env → `.env` → defaults. It
holds the endpoint only: `MODEL`, `BASE_URL`, `API_KEY`, `MAX_RETRIES`, `TIMEOUT`, `THINKING`,
`DRY_RUN` — plus the three paths if you must move them.

The batch knobs above are **not** environment variables: a run changes only because a run said so.

## 5. What a consumer may rely on

- **Existence is the cache.** Anything already written is never rebuilt; a stopped batch resumes
  at the first missing file.
- **Invalidation is deletion.** Editing a template invalidates nothing by itself; a new snapshot
  invalidates what it changed, and `just refresh` is the verb that deletes those profiles.
- **A failure loses nothing.** A failed call writes no file and does not end the batch; the next
  run retries exactly it.
- **A file is whole or absent.** The markdown is written first, the json renamed into place.
- **One turn per file.** No ordering, no dependency, no cascade.
- **The index is optional and derived.** `skills.jsonl` may be absent or older than the tree —
  regenerating it is `just index`, and nothing else ever writes it.
- **The layout is the only contract.** Publish `output/` as it is, snapshot included.

## 6. Open — to agree before this is the spec

1. Are `render` and `test` part of the surface, or dev-only (kept out of the promise above)?
2. Should `snapshot` and `py` be public knobs, or plumbing with a fixed default?
