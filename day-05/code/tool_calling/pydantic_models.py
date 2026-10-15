from typing import Literal
from pydantic import BaseModel, Field

class BranchCutoff(BaseModel):
    program: str = Field(description="e.g. 'B.Tech Computer Science and Engineering' or 'B.Arch Architecture'")
    quota: Literal["HS", "OS", "AI"] = Field(description="HS = home state, OS = other state, AI = all India")
    opening_rank: int | None
    closing_rank: int | None
    source_url: str

class CutoffReport(BaseModel):
    college: str
    exam: str = Field(description="e.g. 'JEE Main'")
    year: int
    round: str | None = Field(description="the counselling round the ranks are from, e.g. 'Round 1'")
    category: str = Field(description="e.g. 'General, Gender-Neutral'")
    cutoffs: list[BranchCutoff]
    notes: str | None = Field(description="anything unclear: missing data, pages that disagree, blocked pages")