#!/usr/bin/env python3
"""Generate one prompt's output for one skill: one call, one json, a markdown copy beside it.

Driven by the justfile (`just one`) - DEVELOPING.md describes the interface it is half of.
"""

import argparse
import json
import re
import sys
from pathlib import Path

import yaml
from jinja2 import Environment, StrictUndefined, TemplateSyntaxError, UndefinedError
from pydantic_settings import BaseSettings, SettingsConfigDict

_env = Environment(autoescape=False, keep_trailing_newline=True, undefined=StrictUndefined)
# The output root holds three layers, and they do not overlap: the skill directories the mirror
# publishes and a user installs, the profiles this project writes about them, and the rest of the
# mirror (its index, repositories, avatars) that the sources were taken from.
SKILLS_DIR = "skills"
PROFILES_DIR = "profiles"
UPSTREAM_DIR = "upstream"
SKILL_MD = "SKILL.md"
SYSTEM_MD = "_system.md"
INDEX = "skills.jsonl"
MAX_SKILL_MD_CHARS = 20000
# A repository can be one skill or several hundred (`awesome-*` collections). The cap keeps the
# context a few thousand characters whatever the repo is, and what was left out is counted.
MAX_SIBLINGS = 50
# A sibling's own description is sometimes a page rather than a line, and a repo of those would
# dwarf the skill's own body. Each is cut to a hint - the opening statement that names the topic,
# which sits well inside this - and the slugs beside them carry the rest.
MAX_SIBLING_CHARS = 300
# libyaml where there is one, which every PyYAML wheel carries, and the pure-Python loader where a
# source build left it out: the block is a few hundred bytes, and a skill is one process.
YAML_LOADER = getattr(yaml, "CSafeLoader", yaml.SafeLoader)
# The header is where a skill's name and description are written down, and both of them are the
# first two parts of the system message already; what sits beside them - `license`, `allowed-tools`,
# a version - is about installing a skill rather than about what it is for. It is cut as one block
# for the body and read as YAML once for the description: a `description:` can be a block scalar or
# a quoted string, so a line-wise read of a header is half a header.
FRONT_MATTER = re.compile(r"\A\s*---\r?\n(.*?)\r?\n---\r?\n", re.S)
# A source that just stops reads as one that ended, and an answer can then be
# confidently wrong about the part that was never sent. Said in the prompt's language,
# and inside the source, so it travels with it.
TRUNCATION_NOTE = "[注: 这份正文过长, 以上仅为开头, 余下内容已省略]"


class Config(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="SKILLS_PROFILES_", env_file=".env", env_file_encoding="utf-8",
        extra="ignore", env_ignore_empty=True)

    model: str = "gpt-4.1-mini"
    base_url: str | None = None
    api_key: str | None = None
    max_retries: int = 3
    timeout: float = 120.0  # per request; the SDK default of ten minutes stalls a worker on a dead connection
    thinking: bool = False
    dry_run: bool = False

    prompts_dir: Path = Path("prompts")
    output_dir: Path = Path("output")


def skill_dir_name(skill: str) -> str:
    """The `_` spelling upstream writes for `:` and `&` in an id."""
    return skill.replace(":", "_").replace("&", "_")


def skill_dir(config: Config, skill: str) -> Path:
    return config.output_dir / PROFILES_DIR / skill_dir_name(skill)


def json_path(config: Config, prompt: str, skill: str) -> Path:
    return skill_dir(config, skill) / f"{prompt}.json"


def markdown_path(config: Config, prompt: str, skill: str) -> Path:
    return skill_dir(config, skill) / "md" / f"{prompt}.md"


def skill_source_path(config: Config, skill: str) -> Path:
    """The skill's own directory as the mirror published it, beside the profile written from it."""
    return config.output_dir / SKILLS_DIR / skill_dir_name(skill) / SKILL_MD


def skill_source(config: Config, skill: str) -> str:
    """The skill's own text, capped at MAX_SKILL_MD_CHARS.

    The cap is what keeps one 290 KB SKILL.md from dominating its request; about one skill
    in ten reaches it. The cut lands on a line break rather than mid-sentence, because a
    heading or a table left in half reads as malformed source, and it is announced,
    because a source that merely stops reads as one that ended.
    """
    text = skill_source_path(config, skill).read_text(encoding="utf-8", errors="replace")
    if len(text) <= MAX_SKILL_MD_CHARS:
        return text
    # the last break that fits, or -1 when one line is longer than the whole budget -
    # then the hard cut is all there is
    cut = text.rfind("\n", 0, MAX_SKILL_MD_CHARS)
    head = text[:cut] if cut > 0 else text[:MAX_SKILL_MD_CHARS]
    return f"{head.rstrip()}\n\n{TRUNCATION_NOTE}\n"


def skill_body(source: str) -> str:
    """The source without its front matter: the part that is not said above it already.

    The name and the description lead the system message, so the copy of them at the top of the file
    is not sent a second time; what sits beside them in the block is metadata about installing a
    skill rather than about what it is for. A source with no front matter to drop is sent as it is: a
    header arriving twice is not a failure, and this is not the place to guess.
    """
    return FRONT_MATTER.sub("", source, count=1).lstrip("\n")


def skill_description(source: str) -> str:
    """The skill's own one-line description: its front matter's `description`, as YAML.

    It is the one part of a skill written to be read on its own, and it is what a prompt leads with,
    so empty means nothing to lead with rather than a description that happens to be short. No front
    matter, a block that is not YAML, and a block with no `description:` all read the same way here,
    and `main` drops the skill on it.
    """
    block = FRONT_MATTER.match(source)
    if block is None:
        return ""
    try:
        front = yaml.load(block.group(1), Loader=YAML_LOADER)
    except yaml.YAMLError:
        return ""
    description = front.get("description") if isinstance(front, dict) else None
    return description.strip() if isinstance(description, str) else ""


def repository(config: Config, skill: str) -> dict | None:
    """The context a skill's own repository gives: its id, and the siblings beside it.

    Upstream nests a skill as `owner/repo/slug`, so the repository is the directory one level above
    the skill's own, and every sibling holds one: no upstream file is read, and a repo that vanished
    upstream still answers. A sibling contributes its own one-line description and nothing else: its
    body would be a second skill's body. A repository with no sibling says nothing the skill's own
    name has not already said, so it is not sent at all rather than sent empty.
    """
    parts = skill_dir_name(skill).split("/")
    if len(parts) != 3:
        return None
    owner, repo, own = parts
    root = config.output_dir / SKILLS_DIR / owner / repo
    if not root.is_dir():
        return None
    siblings = []
    for child in sorted(root.iterdir()):
        source = child / SKILL_MD
        if child.name == own or not source.is_file():
            continue
        one_line = " ".join(skill_description(
            source.read_text(encoding="utf-8", errors="replace")).split())
        if len(one_line) > MAX_SIBLING_CHARS:
            one_line = one_line[:MAX_SIBLING_CHARS].rsplit(" ", 1)[0].rstrip() + "…"
        siblings.append(f"{child.name}: {one_line}" if one_line else child.name)
    if not siblings:
        return None
    return {"id": f"{owner}/{repo}", "siblings": siblings[:MAX_SIBLINGS],
            "more": max(0, len(siblings) - MAX_SIBLINGS)}


def load_prompt(config: Config, prompt: str) -> tuple[str, dict]:
    path = config.prompts_dir / f"{prompt}.md"
    template = path.read_text(encoding="utf-8").strip()
    try:
        _env.parse(template)
    except TemplateSyntaxError as e:
        raise SystemExit(f"{path.name}: invalid jinja2 template, line {e.lineno}: "
                         f"{e.message}") from e
    try:
        # a task template is rendered with no variables: strict catches the one that asks for some
        _env.from_string(template).render()
    except UndefinedError as e:
        raise SystemExit(f"{path.name}: {e}") from e
    schema = json.loads((config.prompts_dir / f"{prompt}.json").read_text(encoding="utf-8"))
    if not isinstance(schema, dict) or schema.get("type") != "object":
        raise SystemExit(f"{prompt}.json: must be a JSON Schema describing an object")
    return template, schema


def render(template: str, body: str, description: str, name: str,
           repo: dict | None = None) -> str:
    return _env.from_string(template).render(
        skill_body=body, description=description, name=name, repo=repo)


def call(config: Config, schema: dict, messages: list[dict]) -> dict:
    if config.dry_run:
        return _placeholder(schema)
    from openai import OpenAI  # imported here so a dry run never loads the SDK

    client = OpenAI(base_url=config.base_url, api_key=config.api_key,
                    max_retries=config.max_retries, timeout=config.timeout)
    kwargs: dict = {
        "model": config.model,
        "messages": messages,
        "response_format": {"type": "json_schema",
                            "json_schema": {"name": "profile", "strict": True,
                                            "schema": schema}},
    }
    if config.thinking:
        # a provider extension rather than an OpenAI field, and `extra_body` is where the
        # SDK forwards one verbatim: as a keyword of its own it is a TypeError, because
        # create() has no `chat_template_kwargs` parameter to accept it
        kwargs["extra_body"] = {"chat_template_kwargs": {"enable_thinking": True}}
    response = client.chat.completions.create(**kwargs)
    text = response.choices[0].message.content
    if not text:
        raise RuntimeError("the model returned an empty message")
    return json.loads(text)


def _placeholder(schema: dict):
    """A value shaped like the schema, so `just DRY=1` writes the real layout."""
    if "enum" in schema:
        return schema["enum"][0]
    kind = schema.get("type")
    if kind == "object":
        return {name: _placeholder(node) for name, node in schema.get("properties", {}).items()}
    if kind == "array":
        return [_placeholder(schema.get("items", {}))
                for _ in range(schema.get("minItems", 1))]
    return "离线演示占位内容"


def write(config: Config, prompt: str, skill: str, output: dict) -> Path:
    md_path = markdown_path(config, prompt, skill)
    md_path.parent.mkdir(parents=True, exist_ok=True)
    md_path.write_text(_markdown(prompt, skill, output), encoding="utf-8")
    path = json_path(config, prompt, skill)
    path.parent.mkdir(parents=True, exist_ok=True)
    # renamed into place: a half-written json would read as "done" to the caller's skip test
    partial = path.with_name(path.name + ".part")
    partial.write_text(json.dumps(output, ensure_ascii=False), encoding="utf-8")
    partial.replace(path)
    return path


def _markdown(prompt: str, skill: str, output: dict) -> str:
    lines = [f"# {skill.rsplit('/', 1)[-1]} (`{skill}`)", "", f"## {prompt}", ""]
    for key, value in output.items():
        lines += [f"### {key}", ""]
        if isinstance(value, list):
            lines += [f"- {_flat(item) if isinstance(item, dict) else item}" for item in value]
        elif isinstance(value, dict):
            lines.append(_flat(value))
        else:
            lines.append(str(value))
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def _flat(pairs: dict) -> str:
    return ", ".join(f"{key}: {value}" for key, value in pairs.items())


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Generate one prompt's output for one skill.")
    parser.add_argument("prompt", help="prompt id, the name of prompts/<id>.md")
    parser.add_argument("skill", help="skill directory in the snapshot, {owner}/{repo}/{slug}")
    parser.add_argument("--print", dest="print_request", action="store_true",
                        help="print the request and stop, calling nothing")
    args = parser.parse_args(argv)

    config = Config()
    try:
        template, schema = load_prompt(config, args.prompt)
        source = skill_source(config, args.skill)
        # The description is the gate on a skill rather than one of its fields: a profile is written
        # from the line saying what the skill is for, so a skill whose own header does not yield one
        # is dropped here - no call, no file - instead of being built from its body alone.
        description = skill_description(source)
        if not description:
            print(f"{args.skill}: no description in its front matter", file=sys.stderr)
            return 1
        # the system prompt is the only template with variables, and it is rendered here rather
        # than in `call`: a name it does not have is a message about that file, not a traceback.
        # The name it leads with is the id - the one handle the tree, the index and a query all
        # use - where the front matter's own `name:` is now and then a shorter spelling of it
        system = render((config.prompts_dir / SYSTEM_MD).read_text(encoding="utf-8").strip(),
                        skill_body(source), description, args.skill)
    except FileNotFoundError as e:
        print(f"{e.filename}: not found", file=sys.stderr)
        return 1
    except UndefinedError as e:
        print(f"{SYSTEM_MD}: {e}", file=sys.stderr)
        return 1

    messages = [
        {"role": "system", "content": system},
        {"role": "user", "content": _env.from_string(template).render()},
    ]
    if args.print_request:
        for message in messages:
            print(f"----- {message['role']} -----\n{message['content']}\n")
        return 0

    output = write(config, args.prompt, args.skill, call(config, schema, messages))
    print(f"built {output}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
