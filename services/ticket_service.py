from datetime import datetime
from sqlalchemy.orm import Session

from database import crud
from database.models import Ticket

def create_ticket(db: Session, user_id: int, title: str, description: str) -> Ticket:
    """Creates a new ticket."""
    new_ticket = Ticket(
        title=title,
        description=description,
        status='open',
        user_id=user_id,
        created_at=datetime.now()
    )
    return crud.save_ticket(db=db, ticket=new_ticket)

def assign_ticket(db: Session, ticket_id: int, support_agent_id: int) -> Ticket | None:
    """
    Assigns a ticket to a support agent.
    Returns the updated ticket or None if the ticket doesn't exist.
    """
    ticket = crud.get_ticket_by_id(db=db, ticket_id=ticket_id)
    if ticket:
        # Ensure the support_agent_id corresponds to a user with 'support' role (validation can be added here or in API layer)
        ticket.status = 'in_progress'
        ticket.support_user_id = support_agent_id  # Use the new field name
        return crud.update_ticket(db=db, ticket_to_update=ticket)
    return None
