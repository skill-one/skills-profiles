"""Names shared by the upstream snapshot and the generated artifact tree.

`skills.jsonl` is the same file name on both sides of the pipeline (upstream
index in, profile index out) and `skills/` the same per-skill directory; keeping
them in one place means a rename cannot leave the reader and the writer apart.
"""

INDEX_NAME = "skills.jsonl"
SKILLS_SUBDIR = "skills"
MD_SUBDIR = "md"


def skill_dir_name(skill_id: str) -> str:
    """The filesystem name of a skill's directory.

    A skill id may carry a colon (`owner/repo/hotel:sub`), which is not portable
    in a path; the snapshot reader and the artifact writer both come through
    here, so the two sides cannot disagree about where a skill lives.
    """
    return skill_id.replace(":", "_")
