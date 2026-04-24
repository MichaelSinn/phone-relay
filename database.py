import os
from sqlalchemy import create_engine, Column, Integer, String, DateTime, Text
from sqlalchemy.orm import declarative_base, sessionmaker
from datetime import datetime, timezone, timedelta
from models import MessageRecord, CallRecord

Base = declarative_base()

class Message(Base):
    __tablename__ = 'messages'
    id = Column(Integer, primary_key=True)
    from_number = Column(String(20))
    to_number = Column(String(20))
    body = Column(Text)
    timestamp = Column(DateTime, default=lambda: datetime.now(timezone.utc))

class Call(Base):
    __tablename__ = 'calls'
    id = Column(Integer, primary_key=True)
    from_number = Column(String(20))
    to_number = Column(String(20))
    timestamp = Column(DateTime, default=lambda: datetime.now(timezone.utc))

DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///relay.db')
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db():
    Base.metadata.create_all(bind=engine)

def save_message(msg_record: MessageRecord):
    db = SessionLocal()
    db_msg = Message(
        from_number=msg_record.from_number,
        to_number=msg_record.to_number,
        body=msg_record.body,
        timestamp=msg_record.timestamp
    )
    db.add(db_msg)
    db.commit()
    db.refresh(db_msg)
    db.close()
    return db_msg

def save_call(call_record: CallRecord):
    db = SessionLocal()
    db_call = Call(
        from_number=call_record.from_number,
        to_number=call_record.to_number,
        timestamp=call_record.timestamp
    )
    db.add(db_call)
    db.commit()
    db.refresh(db_call)
    db.close()
    return db_call

def get_last_sender_by_last_four(last_four: str, to_number: str):
    db = SessionLocal()
    result = db.query(Message).filter(
        Message.to_number == to_number,
        Message.from_number.like(f'%{last_four}')
    ).order_by(Message.timestamp.desc()).first()
    db.close()
    return result.from_number if result else None

def has_recent_activity(days: int = 7):
    """Check if there has been any message activity in the last `days`."""
    db = SessionLocal()
    cutoff = datetime.now(timezone.utc) - timedelta(days=days)
    result = db.query(Message).filter(Message.timestamp >= cutoff).first()
    db.close()
    return result is not None
