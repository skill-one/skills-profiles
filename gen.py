#!/usr/bin/env python3
"""Generate one prompt's output for one skill: one call, one json, a markdown copy beside it.

Driven by the justfile (`just one`) - DEVELOPING.md describes the interface it is half of.
"""

import argparse
import json
import sys
from pathlib import Path

from jinja2 import Environment, StrictUndefined, TemplateSyntaxError, UndefinedError
from pydantic_settings import BaseSettings, SettingsConfigDict

_env = Environment(autoescape=False, keep_trailing_newline=True, undefined=StrictUndefined)
SKILLS_DIR = "skills"
SKILL_MD = "SKILL.md"
MAX_SKILL_MD_CHARS = 20000
# A source that just stops reads as one that ended, and an answer can then be
# confidently wrong about the part that was never sent. Said in the prompt's language,
# and inside the source, so it travels with it.
TRUNCATION_NOTE = "[注: 这份 skill.md 过长, 以上仅为开头, 余下内容已省略]"


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

    data_dir: Path = Path("output/cache/skills-sh")
    prompts_dir: Path = Path("prompts")
    output_dir: Path = Path("output")


def skill_dir_name(skill: str) -> str:
    """The `_` spelling upstream writes for `:` and `&` in an id."""
    return skill.replace(":", "_").replace("&", "_")


def skill_dir(config: Config, skill: str) -> Path:
    return config.output_dir / SKILLS_DIR / skill_dir_name(skill)


def json_path(config: Config, prompt: str, skill: str) -> Path:
    return skill_dir(config, skill) / f"{prompt}.json"


def markdown_path(config: Config, prompt: str, skill: str) -> Path:
    return skill_dir(config, skill) / "md" / f"{prompt}.md"


def skill_source_path(config: Config, skill: str) -> Path:
    return config.data_dir / SKILLS_DIR / skill_dir_name(skill) / SKILL_MD


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


def render(template: str, source: str) -> str:
    return _env.from_string(template).render(skill_md=source)


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
        system = (config.prompts_dir / "_system.md").read_text(encoding="utf-8").strip()
    except FileNotFoundError as e:
        print(f"{e.filename}: not found", file=sys.stderr)
        return 1
    except UndefinedError as e:
        print(f"_system.md: {e}", file=sys.stderr)
        return 1

    messages = [
        {"role": "system", "content": render(system, source)},
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
