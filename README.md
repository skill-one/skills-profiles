# skills-profiles

The agent skills this repository collects, each labelled with one closed-domain
category by the Jev endpoint and described in Chinese by a chat model, plus the
catalog joining it all. Written by `just index` - generated, so do not edit it.
中文: [README.zh-CN.md](README.zh-CN.md)

`skills/<id>/` is the source page every angle was built from; the full skill lives
in its own repository. `profiles/<id>/` holds what
is written about it - the domain label, the Chinese `description_zh`, and the
Chinese `skill_zh` page - and `skills.jsonl` is the catalog joining them.

## Progress

- **domain**: 8928 of 9006 labelled (99.1%), covering 100.0% of the mirror's installs
- **translate**: 8908 of 9006 translated (98.9%), covering 99.9% of the mirror's installs
- **skill_zh**: 1361 of 9006 skill pages translated (15.1%), covering 83.7% of the mirror's installs
- **snapshot**: `dist-2026-09-24`, 2026-09-24T20:52:29Z -> 2026-09-24T21:22:24Z (29m54s)
- **buildable**: 9006 of 9028 have a readable description; the rest are never built
