"""Resume text analytics API.

Uses extracted PDF text from disk only — do not import ``app.services.vectors`` or Chroma here.
"""

from fastapi import APIRouter, Query

from app.services.resume_analytics import ResumeAnalyticsResponse, compute_resume_analytics

router = APIRouter(prefix="/api/resumes", tags=["resume analytics"])


@router.get("/analytics", response_model=ResumeAnalyticsResponse)
def get_analytics(
    top_skills: int = Query(default=15, ge=1, le=200),
    include_other: bool = Query(
        default=True,
        description="If false, omits the 'Other' category from the pie chart data.",
    ),
) -> ResumeAnalyticsResponse:
    return compute_resume_analytics(top_skills=top_skills, include_other=include_other)
