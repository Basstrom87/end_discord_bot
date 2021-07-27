from sqlalchemy import Column
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.dialects.sqlite import DATETIME, INTEGER, TEXT

Base = declarative_base()


class Event(Base):
    __tablename__ = 'event'
    __table_args__ = {'sqlite_autoincrement': True}
    id = Column(INTEGER, primary_key=True, nullable=False)
    name = Column(TEXT)
    server = Column(TEXT)
    date = Column(DATETIME)


class Attendance(Base):
    __tablename__ = 'attendance'
    __table_args__ = {'sqlite_autoincrement': True}
    id = Column(INTEGER, primary_key=True, nullable=False)
    member_id = Column(INTEGER)
    event_id = Column(INTEGER)
    attendance = Column(TEXT)


class Member(Base):
    __tablename__ = 'member'
    id = Column(INTEGER, primary_key=True, nullable=False)
    name = Column(TEXT)
    active = Column(TEXT)
    time_zone = Column(TEXT)
