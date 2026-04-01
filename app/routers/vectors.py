from fastapi import APIRouter, HTTPException, Query

from app.services.vectors import (
    NeighborRequest,
    NeighborResponse,
    ProjectionRequest,
    ProjectionResponse,
    export_vectors,
    find_neighbors,
    project_embeddings,
)

router = APIRouter(prefix="/api/vectors", tags=["vectors"])


@router.get("/export")
def export(max_points: int = Query(default=5000, gt=0)) -> dict:
    return export_vectors(max_points=max_points)


@router.post("/project", response_model=ProjectionResponse)
def project(request: ProjectionRequest) -> ProjectionResponse:
    if len(request.embeddings) < 2:
        raise HTTPException(
            status_code=422,
            detail="At least 2 embeddings are required for UMAP projection",
        )
    return project_embeddings(request.embeddings, request.n_clusters)


@router.post("/neighbors", response_model=NeighborResponse)
def neighbors(request: NeighborRequest) -> NeighborResponse:
    return find_neighbors(request.query, request.k)
