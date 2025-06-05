from sqlalchemy.orm import Session
from . import models

# Ticket CRUD operations

def get_ticket_by_id(db: Session, ticket_id: int) -> models.Ticket | None:
    """Retrieves a ticket by its ID."""
    return db.query(models.Ticket).filter(models.Ticket.id == ticket_id).first()

def get_all_tickets(db: Session, skip: int = 0, limit: int = 100) -> list[models.Ticket]:
    """Retrieves a list of tickets with pagination."""
    return db.query(models.Ticket).offset(skip).limit(limit).all()

def get_tickets_by_user_id_crud(db: Session, user_id: int, skip: int = 0, limit: int = 100) -> list[models.Ticket]:
    """Retrieves all tickets for a specific user ID from the database."""
    return db.query(models.Ticket).filter(models.Ticket.user_id == user_id).order_by(models.Ticket.created_at.desc()).offset(skip).limit(limit).all()

def count_tickets_by_user_id(db: Session, user_id: int) -> int:
    """Counts all tickets for a specific user ID in the database."""
    return db.query(models.Ticket).filter(models.Ticket.user_id == user_id).count()

def count_all_tickets(db: Session) -> int:
    """Counts all tickets in the database."""
    return db.query(models.Ticket).count()

def save_ticket(db: Session, ticket: models.Ticket) -> models.Ticket:
    """Saves a new ticket to the database."""
    db.add(ticket)
    db.commit()
    db.refresh(ticket)
    return ticket

def update_ticket(db: Session, ticket_to_update: models.Ticket) -> models.Ticket:
    """
    Updates an existing ticket.
    Assumes 'ticket_to_update' is an ORM object fetched via the same session 'db'
    and has been modified in memory. Committing the session persists these changes.
    """
    db.commit() # The object is already dirty in the session, commit flushes changes.
    db.refresh(ticket_to_update) # Refresh to get any DB-side updates.
    return ticket_to_update

def delete_ticket(db: Session, ticket_id: int) -> models.Ticket | None:
    """Deletes a ticket by its ID. Returns the deleted ticket or None if not found."""
    ticket = db.query(models.Ticket).filter(models.Ticket.id == ticket_id).first()
    if ticket:
        db.delete(ticket)
        db.commit()
    return ticket

# User CRUD operations

def get_user_by_id(db: Session, user_id: int) -> models.User | None:
    """Retrieves a user by their internal ID."""
    return db.query(models.User).filter(models.User.id == user_id).first()

def get_user_by_telegram_id(db: Session, telegram_id: int) -> models.User | None:
    """Retrieves a user by their Telegram ID."""
    return db.query(models.User).filter(models.User.telegram_id == telegram_id).first()

def get_all_users(db: Session, skip: int = 0, limit: int = 100) -> list[models.User]:
    """Retrieves a list of users with pagination."""
    return db.query(models.User).offset(skip).limit(limit).all()

def create_user(db: Session, user: models.User) -> models.User:
    """Creates a new user."""
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

def update_user(db: Session, user_to_update: models.User) -> models.User:
    """
    Updates an existing user.
    Assumes 'user_to_update' is an ORM object fetched via the same session 'db'
    and has been modified in memory.
    """
    db.commit()
    db.refresh(user_to_update)
    return user_to_update

def delete_user(db: Session, user_id: int) -> models.User | None:
    """Deletes a user by their ID. Returns the deleted user or None if not found."""
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if user:
        db.delete(user)
        db.commit()
    return user