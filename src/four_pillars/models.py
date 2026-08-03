from __future__ import annotations

from datetime import date, datetime
from enum import StrEnum
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator


class Gender(StrEnum):
    MALE = "male"
    FEMALE = "female"
    UNSPECIFIED = "unspecified"


class CalendarKind(StrEnum):
    SOLAR = "solar"
    LUNAR = "lunar"


class TimeBasis(StrEnum):
    CIVIL = "civil"
    MEAN_SOLAR = "mean_solar"
    APPARENT_SOLAR = "apparent_solar"


class DayBoundary(StrEnum):
    MIDNIGHT = "midnight"
    LATE_ZI = "late_zi"


class BirthInput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    birth: datetime
    timezone: str = "Asia/Seoul"
    gender: Gender = Gender.UNSPECIFIED
    calendar: CalendarKind = CalendarKind.SOLAR
    lunar_leap_month: bool = False
    birth_time_known: bool = True
    longitude: float | None = Field(default=None, ge=-180, le=180)
    time_basis: TimeBasis = TimeBasis.CIVIL
    day_boundary: DayBoundary = DayBoundary.MIDNIGHT

    @field_validator("birth")
    @classmethod
    def reject_timezone_on_wall_clock(cls, value: datetime) -> datetime:
        if value.tzinfo is not None:
            return value.replace(tzinfo=None)
        return value


class Pillar(BaseModel):
    model_config = ConfigDict(frozen=True)

    stem_index: int = Field(ge=0, le=9)
    branch_index: int = Field(ge=0, le=11)
    stem: str
    branch: str
    korean: str
    hanja: str
    sexagenary_index: int = Field(ge=0, le=59)
    ten_god: str | None = None
    hidden_stems: tuple[str, ...] = ()
    hidden_ten_gods: tuple[str, ...] = ()
    growth_stage: str | None = None


class SolarTerm(BaseModel):
    model_config = ConfigDict(frozen=True)

    name_ko: str
    name_hanja: str
    longitude: float
    occurs_at: datetime
    month_branch_index: int


class Interaction(BaseModel):
    kind: Literal["stem_combine", "stem_clash", "branch_combine", "branch_clash", "branch_harm"]
    left: str
    right: str
    description: str


class Chart(BaseModel):
    model_config = ConfigDict(extra="forbid")

    normalized_birth: datetime
    timezone: str
    calendar_input: CalendarKind
    time_basis: TimeBasis
    day_boundary: DayBoundary
    birth_time_known: bool
    year: Pillar
    month: Pillar
    day: Pillar
    hour: Pillar | None
    day_master: str
    element_balance: dict[str, float]
    interactions: list[Interaction]
    current_jie: SolarTerm
    next_jie: SolarTerm
    boundary_warnings: list[str]
    calculation_version: str = "calendar-1.0.0"
    fingerprint: str


class LuckPeriod(BaseModel):
    sequence: int
    direction: Literal["forward", "reverse"]
    pillar: Pillar
    start_age: float
    end_age: float
    starts_at: date
    ends_at: date
    interactions: list[Interaction] = []


class DaewoonScenario(BaseModel):
    label: str
    direction: Literal["forward", "reverse"]
    start_age: float
    periods: list[LuckPeriod]
    warning: str | None = None


class DaewoonResult(BaseModel):
    scenarios: list[DaewoonScenario]


class LuckSnapshot(BaseModel):
    label: str
    starts_at: datetime
    ends_at: datetime
    pillar: Pillar
    interactions: list[Interaction]
    boundary_warnings: list[str] = []


class ReportSection(BaseModel):
    model_config = ConfigDict(extra="forbid")

    title: str
    summary: str
    opportunities: list[str] = Field(min_length=1)
    cautions: list[str] = Field(min_length=1)
    actions: list[str] = Field(min_length=1)
    examples: list[str] = []
    evidence: list[str] = []


class PracticalSkill(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str
    purpose: str
    steps: list[str] = Field(min_length=2)
    when_to_use: str


class ReportDocument(BaseModel):
    model_config = ConfigDict(extra="forbid")

    subject_name: str
    title: str
    executive_summary: str
    calculation_fingerprint: str
    sections: dict[str, ReportSection]
    practical_skills: list[PracticalSkill]
    disclaimer: str
    generated_at: datetime
    model: str
    prompt_versions: dict[str, str]
    quality_notes: list[str] = []


class JobStatus(StrEnum):
    QUEUED = "queued"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    QUALITY_FAILED = "quality_failed"


class ReportJob(BaseModel):
    id: str
    status: JobStatus
    request: dict[str, Any]
    created_at: datetime
    updated_at: datetime
    error: str | None = None
    artifact_dir: str | None = None
