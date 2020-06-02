from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from apollo.lib.schemas.agent import CreateAgentSchema
from apollo.models import get_session, save
from apollo.models.agent import Agent

router = APIRouter()


@router.post("/agent")
def post_agent(agent_data: CreateAgentSchema,
               session: Session = Depends(get_session)):
    save(session, Agent(**dict(agent_data)))
