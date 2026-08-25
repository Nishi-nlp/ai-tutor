from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.schemas.knowledge_component import KnowledgeComponentResponse
from app.db import knowledge_components as knowledge_component_repository
from app.db.session import get_db_session

router = APIRouter(prefix="/api/kcs", tags=["knowledge-components"])


@router.get("/{kc_id}", response_model=KnowledgeComponentResponse)
def get_knowledge_component(
    kc_id: str,
    session: Annotated[Session, Depends(get_db_session)],
) -> KnowledgeComponentResponse:
    knowledge_component = knowledge_component_repository.get_by_id(session, kc_id)

    if knowledge_component is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Knowledge component not found",
        )

    return KnowledgeComponentResponse.model_validate(knowledge_component)
