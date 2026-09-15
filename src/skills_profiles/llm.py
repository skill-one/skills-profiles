"""LLM client factory, the shared RPM bucket, and an offline fake for dry-runs."""

import instructor
from aiolimiter import AsyncLimiter
from openai import AsyncOpenAI

from . import models as m
from .config import Settings


class RateLimitedLLM:
    """Paces `create()` call starts through one shared per-minute bucket.

    Agnes documents 20 RPM for its chat models (see `Settings.llm_rate_limit`);
    unlike the concurrency semaphore's in-flight ceiling this bounds how many
    request *starts* a run may make per minute, however many skills are in
    flight. The bucket is released before the call itself, so a slow request
    does not consume a second slot of quota — RPM counts starts.
    """

    def __init__(self, inner, rate: int, window: int = 60) -> None:
        self.inner = inner
        self._limiter = AsyncLimiter(rate, window) if rate else None

    async def create(self, response_model=None, messages=None, **kwargs):
        if self._limiter is not None:
            async with self._limiter:
                pass  # acquiring the slot is the accounting, nothing more
        return await self.inner.create(response_model, messages, **kwargs)


def make_llm(settings: Settings) -> RateLimitedLLM:
    """instructor-patched async client behind the shared RPM bucket."""
    client = AsyncOpenAI(base_url=settings.base_url, api_key=settings.api_key)
    return RateLimitedLLM(instructor.from_openai(client), settings.llm_rate_limit)


# The stand-in name the fake writes into its Chinese prose. Fixed on purpose: the
# fake never reads the prompt, so a dry-run stays byte-identical however the
# templates change.
FAKE_NAME = "该 skill"


class FakeLLM:
    """Deterministic offline stand-in for dry-runs and tests."""

    async def create(self, response_model, messages=None, **kwargs):
        return _fake_output(response_model)


def _fake_output(model):
    if model is m.DomainClassification:
        return m.DomainClassification(domain=m.Domain.OFFICE, reason="离线演示用的固定分类")
    if model is m.IntroText:
        return m.IntroText(text=f"{FAKE_NAME} 的离线演示档案文本, 用于验证管道, 不含真实内容。")
    if model is m.BlackBoxIntro:
        return m.BlackBoxIntro(
            function=f"{FAKE_NAME} 的离线演示功能描述",
            input_output=[
                m.BlackBoxPair(input="输入 A", output=f"{FAKE_NAME} 的结果 1"),
                m.BlackBoxPair(input="输入 B", output="结果 2"),
            ],
        )
    if model is m.WhiteBoxIntro:
        return m.WhiteBoxIntro(
            execution_flow=[f"{FAKE_NAME} 被触发后先做步骤 1", "再做步骤 2", "最后完成步骤 3"],
            mechanisms=["通过离线演示机制完成任务, 不依赖外部资源"],
        )
    if model is m.Taglines:
        return m.Taglines(taglines=[f"{FAKE_NAME}, 简单高效", "让 agent 更能干", "省时省力的好帮手"])
    if model is m.Persona:
        return m.Persona(
            tool="扳手",
            pitch=f"我替你把 {FAKE_NAME} 的活干完, 还你一个能用的结果——我是一把扳手",
        )
    if model is m.ImagePrompt:
        # obeys the schema's rejection rules: ASCII, leading "one ", <= 40 words
        return m.ImagePrompt(
            text="one sturdy chrome wrench, glowing open jaw as focal point, "
                 "knurled handle, polished chrome body")
    if model is m.SkillComments:
        return m.SkillComments(comments=[
            m.SkillComment(user="后端老兵", category="妙用",
                           comment=f"我发现 {FAKE_NAME} 能直接接进现有流程, 省了一步手工操作"),
            m.SkillComment(user="第一次用的新手", category="坑",
                           comment="我一开始没看前置条件就直接跑, 果然失败了"),
            m.SkillComment(user="运维老哥", category="注意",
                           comment=f"用 {FAKE_NAME} 之前先确认环境配置, 我在这里卡过"),
        ])
    raise TypeError(f"FakeLLM cannot handle {model}")
