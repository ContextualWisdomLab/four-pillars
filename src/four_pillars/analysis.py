from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

from pydantic import BaseModel, Field

from .models import (
    Chart,
    DaewoonResult,
    LuckSnapshot,
    PracticalSkill,
    ReportDocument,
    ReportSection,
)
from .nim import NimClient, NimTrace
from .prompts import PROMPT_NAMES, load_prompt
from .quality import ReportQualityError, assert_report_quality


class PracticalSkillsDraft(BaseModel):
    practical_skills: list[PracticalSkill] = Field(min_length=1, max_length=8)


class SynthesisDraft(BaseModel):
    executive_summary: str
    sections: dict[str, ReportSection]
    disclaimer: str


class GeneratedReport(BaseModel):
    report: ReportDocument
    traces: dict[str, dict[str, Any]]


def _trace_payload(trace: NimTrace) -> dict[str, Any]:
    return {
        "model": trace.model,
        "attempts": trace.attempts,
        "repairs": trace.repairs,
    }


async def generate_report(
    *,
    client: NimClient,
    subject_name: str,
    chart: Chart,
    daewoon: DaewoonResult,
    annual: LuckSnapshot,
    monthly: LuckSnapshot,
    user_context: str = "",
) -> GeneratedReport:
    immutable = {
        "chart": chart.model_dump(mode="json"),
        "daewoon": daewoon.model_dump(mode="json"),
        "annual": annual.model_dump(mode="json"),
        "monthly": monthly.model_dump(mode="json"),
        "calculation_fingerprint": chart.fingerprint,
    }
    context = {"user_context": user_context}
    traces: dict[str, dict[str, Any]] = {}

    async def section(name: str, payload: dict[str, Any]) -> ReportSection:
        prompt = load_prompt(name)
        result, trace = await client.generate(
            system_prompt=prompt.body,
            user_payload=payload,
            response_model=ReportSection,
        )
        traces[name] = _trace_payload(trace)
        return result

    natal = await section("natal_analysis", {"calculation": immutable["chart"], **context})
    daewoon_section = await section(
        "daewoon_analysis",
        {"calculation": {"chart": immutable["chart"], "daewoon": immutable["daewoon"]}, **context},
    )
    annual_section = await section(
        "annual_analysis",
        {
            "calculation": {
                "chart": immutable["chart"],
                "daewoon": immutable["daewoon"],
                "annual": immutable["annual"],
            },
            **context,
        },
    )
    monthly_section = await section(
        "monthly_analysis",
        {"calculation": immutable, **context},
    )

    practical_prompt = load_prompt("practical_skills")
    practical, practical_trace = await client.generate(
        system_prompt=practical_prompt.body,
        user_payload={
            "monthly_analysis": monthly_section.model_dump(mode="json"),
            "annual_analysis": annual_section.model_dump(mode="json"),
            **context,
        },
        response_model=PracticalSkillsDraft,
    )
    traces["practical_skills"] = _trace_payload(practical_trace)

    synthesis_prompt = load_prompt("synthesis")
    synthesis, synthesis_trace = await client.generate(
        system_prompt=synthesis_prompt.body,
        user_payload={
            "calculation": immutable,
            "drafts": {
                "natal": natal.model_dump(mode="json"),
                "daewoon": daewoon_section.model_dump(mode="json"),
                "annual": annual_section.model_dump(mode="json"),
                "monthly": monthly_section.model_dump(mode="json"),
                "practical_skills": practical.model_dump(mode="json"),
            },
            **context,
        },
        response_model=SynthesisDraft,
        max_tokens=8192,
    )
    traces["synthesis"] = _trace_payload(synthesis_trace)
    prompt_versions = {name: load_prompt(name).version for name in PROMPT_NAMES}
    report = ReportDocument(
        subject_name=subject_name,
        title=f"{subject_name} 사주 보고서",
        executive_summary=synthesis.executive_summary,
        calculation_fingerprint=chart.fingerprint,
        sections=synthesis.sections,
        practical_skills=practical.practical_skills,
        disclaimer=synthesis.disclaimer,
        generated_at=datetime.now(UTC),
        model=synthesis_trace.model,
        prompt_versions=prompt_versions,
    )

    try:
        assert_report_quality(report, chart.fingerprint)
    except ReportQualityError as error:
        repair_prompt = load_prompt("editorial_repair")
        repaired, repair_trace = await client.generate(
            system_prompt=repair_prompt.body,
            user_payload={
                "calculation": immutable,
                "report": report.model_dump(mode="json"),
                "violations": [issue.__dict__ for issue in error.issues],
            },
            response_model=ReportDocument,
            temperature=0,
            max_tokens=8192,
        )
        traces["editorial_repair"] = _trace_payload(repair_trace)
        report = repaired.model_copy(
            update={
                "subject_name": subject_name,
                "title": f"{subject_name} 사주 보고서",
                "calculation_fingerprint": chart.fingerprint,
                "generated_at": datetime.now(UTC),
                "model": repair_trace.model,
                "prompt_versions": prompt_versions,
                "quality_notes": [issue.message for issue in error.issues],
            }
        )
        assert_report_quality(report, chart.fingerprint)

    return GeneratedReport(report=report, traces=traces)
