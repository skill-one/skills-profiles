"""LLM client factory and an offline fake for dry-runs."""

import instructor
from instructor import Instructor
from openai import AsyncOpenAI

from .config import Settings


def make_llm(settings: Settings) -> Instructor:
    """instructor-patched async client; supports any OpenAI-compatible endpoint."""
    client = AsyncOpenAI(base_url=settings.base_url, api_key=settings.api_key)
    return instructor.from_openai(client)


class FakeLLM:
    """Deterministic offline stand-in for dry-runs and tests."""

    async def create(self, response_model, messages=None, **kwargs):
        system = messages[0]["content"] if messages else ""
        name = "该 skill"
        for line in system.splitlines():
            if line.startswith("skill 名称:"):
                name = line.removeprefix("skill 名称:").strip()
                break
        return _fake_output(response_model, name)


def _fake_output(model, name: str):
    from . import models as m

    if model is m.DomainClassification:
        return m.DomainClassification(domain=m.Domain.OFFICE, reason="离线演示用的固定分类")
    if model is m.IntroText:
        return m.IntroText(text=f"{name} 的离线演示档案文本, 用于验证管道, 不含真实内容。")
    if model is m.BlackBoxIntro:
        return m.BlackBoxIntro(
            function=f"{name} 的离线演示功能描述",
            input_output=[
                m.BlackBoxPair(input="输入 A", output=f"{name} 的结果 1"),
                m.BlackBoxPair(input="输入 B", output="结果 2"),
            ],
        )
    if model is m.WhiteBoxIntro:
        return m.WhiteBoxIntro(
            execution_flow=[f"{name} 被触发后先做步骤 1", "再做步骤 2", "最后完成步骤 3"],
            mechanisms=["通过离线演示机制完成任务, 不依赖外部资源"],
        )
    if model is m.Taglines:
        return m.Taglines(taglines=[f"{name}, 简单高效", "让 agent 更能干", "省时省力的好帮手"])
    if model is m.Persona:
        return m.Persona(
            tool="扳手",
            pitch=f"我替你把 {name} 的活做完, 还你一个能用的结果——我是一把扳手",
        )
    if model is m.ImagePrompt:
        # ASCII only: the schema rejects a Chinese recipe, so the fake must obey it too
        return m.ImagePrompt(
            text="a sturdy chrome wrench, boxy head, knurled straight handle, "
                 "slightly open jaws, lying at a slight angle")
    if model is m.SkillComments:
        return m.SkillComments(comments=[
            m.SkillComment(user="后端老兵", category="妙用", comment=f"我发现 {name} 能直接接进现有流程, 省了一步手工操作"),
            m.SkillComment(user="第一次用的新手", category="坑", comment="我一开始没看前置条件就直接跑, 果然失败了"),
            m.SkillComment(user="运维老哥", category="注意", comment=f"用 {name} 之前先确认环境配置, 我在这里卡过"),
        ])
    raise TypeError(f"FakeLLM cannot handle {model}")
