# skills-profiles

The agent skills this repository collects, each labelled with one closed-domain
category by the Jev endpoint and described in Chinese by a chat model, plus the
catalog joining it all. Written by `just index` - generated, so do not edit it.
中文: [README.zh-CN.md](README.zh-CN.md)

`skills/<id>/` is the source page every angle was built from; the full skill lives
in its own repository, at the `url` the catalog names. `profiles/<id>/` holds what
is written about it - the domain label, the Chinese `description_zh`, and the
Chinese `skill_zh` page - and `skills.jsonl` is the catalog joining them.

## Progress

- **domain**: 9006 of 9007 labelled (100.0%), covering 100.0% of the mirror's installs
- **translate**: 8986 of 9007 translated (99.8%), covering 99.9% of the mirror's installs
- **skill_zh**: 237 of 9007 skill pages translated (2.6%), covering 49.3% of the mirror's installs
- **snapshot**: `dist-2026-09-21`, 2026-09-21T21:18:59Z -> 2026-09-21T21:49:08Z (30m09s)
- **buildable**: 9007 of 9029 have a readable description; the rest are never built
