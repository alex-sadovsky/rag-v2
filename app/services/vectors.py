import random
from typing import Optional

import numpy as np
import umap
from pydantic import BaseModel, field_validator
from sklearn.cluster import KMeans

from app.services.rag import _get_embeddings, get_vectorstore


# ---------------------------------------------------------------------------
# Pydantic models
# ---------------------------------------------------------------------------


class ProjectionRequest(BaseModel):
    embeddings: list[list[float]]
    n_clusters: Optional[int] = None

    @field_validator("embeddings")
    @classmethod
    def at_least_two(cls, v: list) -> list:
        if len(v) < 2:
            raise ValueError("At least 2 embeddings are required for UMAP projection")
        return v


class ProjectionResponse(BaseModel):
    coords: list[list[float]]
    cluster_labels: Optional[list[int]] = None


class NeighborRequest(BaseModel):
    query: str
    k: int = 5

    @field_validator("query")
    @classmethod
    def non_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("query must not be empty")
        return v


class NeighborResponse(BaseModel):
    neighbor_ids: list[str]
    distances: list[float]
    k_actual: int


# ---------------------------------------------------------------------------
# Service functions
# ---------------------------------------------------------------------------


def export_vectors(max_points: int = 5000) -> dict:
    vs = get_vectorstore()
    result = vs._collection.get(include=["embeddings", "documents", "metadatas"])

    ids: list = result.get("ids") or []
    embeddings = result.get("embeddings")
    if embeddings is None:
        embeddings = []
    else:
        embeddings = [e.tolist() if hasattr(e, "tolist") else list(e) for e in embeddings]
    documents: list = result.get("documents") or []
    metadatas: list = result.get("metadatas") or []

    if not ids:
        return {
            "ids": [],
            "embeddings": [],
            "documents": [],
            "metadatas": [],
            "sampled": False,
            "warning": "Collection is empty",
        }

    sampled = False
    if len(ids) > max_points:
        indices = random.sample(range(len(ids)), max_points)
        ids = [ids[i] for i in indices]
        embeddings = [embeddings[i] for i in indices]
        documents = [documents[i] for i in indices]
        metadatas = [metadatas[i] for i in indices]
        sampled = True

    return {
        "ids": ids,
        "embeddings": embeddings,
        "documents": documents,
        "metadatas": metadatas,
        "sampled": sampled,
    }


def project_embeddings(
    embeddings: list[list[float]], n_clusters: Optional[int] = None
) -> ProjectionResponse:
    arr = np.array(embeddings, dtype=np.float32)
    reducer = umap.UMAP(n_components=2, n_neighbors=15, min_dist=0.1, random_state=42)
    coords_2d = reducer.fit_transform(arr).tolist()

    cluster_labels = None
    if n_clusters is not None:
        k = min(n_clusters, len(embeddings))
        km = KMeans(n_clusters=k, random_state=42, n_init="auto")
        cluster_labels = km.fit_predict(arr).tolist()

    return ProjectionResponse(coords=coords_2d, cluster_labels=cluster_labels)


def find_neighbors(query: str, k: int) -> NeighborResponse:
    vs = get_vectorstore()
    collection_size = vs._collection.count()
    k_actual = min(k, collection_size)

    results = vs._collection.query(
        query_embeddings=[_get_embeddings().embed_query(query)],
        n_results=k_actual,
        include=["distances"],
    )

    neighbor_ids = results["ids"][0] if results["ids"] else []
    distances = results["distances"][0] if results["distances"] else []

    return NeighborResponse(
        neighbor_ids=neighbor_ids,
        distances=distances,
        k_actual=k_actual,
    )
