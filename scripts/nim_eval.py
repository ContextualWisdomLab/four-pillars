"""Run the opt-in hosted NVIDIA NIM report-quality evaluation fixture."""

from __future__ import annotations

import asyncio
import json
import os
from datetime import UTC, datetime

from pydantic import BaseModel

from four_pillars.models import PracticalSkill, ReportDocument, ReportSection
from four_pillars.nim import NimClient
from four_pillars.prompts import load_prompt
from four_pillars.settings import Settings


class JudgeResult(BaseModel):
    """Structured scores and findings returned by the NIM quality judge."""

    scores: dict[str, int]
    passed: bool
    findings: list[str]


def fixture_report() -> ReportDocument:
    """Build a deterministic Korean report fixture for hosted judge evaluation."""
    keys = ("natal", "daewoon", "annual", "monthly", "work", "money", "relationships", "daily_rhythm")
    sections = {
        key: ReportSection(
            title=key,
            summary="혜지 님은 계산 근거와 현실 조건을 함께 비교합니다.",
            opportunities=["구체적인 합의를 통해 신뢰와 협력을 높일 수 있습니다."],
            cautions=["피로한 상태에서 중요한 결정을 서두르지 않습니다."],
            actions=["담당 범위, 기한, 지원, 보상을 문서로 확인합니다."],
            evidence=["월운 丙申"],
        )
        for key in keys
    }
    return ReportDocument(
        subject_name="평가 대상",
        title="평가용 사주 보고서",
        executive_summary="독자는 결정론적 계산과 상징 해석을 구분합니다.",
        calculation_fingerprint="a" * 64,
        sections=sections,
        practical_skills=[
            PracticalSkill(
                name="주간 캘린더 검토",
                purpose="일정 충돌과 완충 시간을 미리 확인합니다.",
                steps=["확정 일정을 표시합니다.", "가안 일정에 판단일을 적습니다."],
                when_to_use="매주 한 번 사용합니다.",
            )
        ],
        disclaimer="이 보고서는 전통 명리학의 상징 자료입니다. 의학·법률·재정 판단은 실제 정보와 전문가 의견을 우선합니다.",
        generated_at=datetime.now(UTC),
        model="fixture",
        prompt_versions={"llm_judge": "1.0.0"},
    )


async def main() -> None:
    """Call the configured hosted judge and exit unsuccessfully when it rejects the fixture."""
    if not os.getenv("NVIDIA_NIM_API_KEY"):
        raise SystemExit("NVIDIA_NIM_API_KEY is required for live NIM evaluation")
    settings = Settings()
    prompt = load_prompt("llm_judge")
    async with NimClient(settings) as client:
        result, trace = await client.generate(
            system_prompt=prompt.body,
            user_payload={
                "calculation": {"fingerprint": "a" * 64, "monthly_pillar": "丙申"},
                "report": fixture_report().model_dump(mode="json"),
            },
            response_model=JudgeResult,
            model=settings.nim_eval_model,
            temperature=0,
            max_tokens=1024,
        )
    print(json.dumps({"result": result.model_dump(), "trace": trace.__dict__}, ensure_ascii=False, indent=2))
    if not result.passed:
        raise SystemExit("NIM judge did not pass the committed fixture")


if __name__ == "__main__":
    asyncio.run(main())
