from pprint import pprint
from sqlalchemy import engine, create_engine
from sqlalchemy.orm import sessionmaker
from models import Base, Event, Member, Attendance
from random import randint

# Database Connection
engine = create_engine('sqlite:///event-bot.db', echo=False)
Session = sessionmaker(bind=engine)
session = Session()


def add_attendee(name: str, attendee: str):
    author = name
    id = randint(1, 100000000000000)
    try:
        count = session.query(Member).filter(Member.id == id).count()
        event = session.query(Event).filter(Event.name == name).first()

        # Verify This event exists
        if not event:
            print("Event Does Not Exist")
            return

        # Create member if they do not exist in our database
        if count < 1:
            member = Member(id=id, name=attendee)
            session.add(member)

        attending = Attendance(member_id=id, event_id=event.id)
        session.add(attending)
        session.commit()
    except Exception as e:
        print('Oh Shit something went wrong')
        print(e)


def print_attendees(name: str):
    event = session.query(Event).filter(Event.name == name).first()
    # Number of people attending
    attending = session.query(Attendance).filter(Attendance.event_id == event.id).count()
    attendees = session.query(Member, Attendance).filter(Member.id == Attendance.member_id).filter(Attendance.event_id == event.id)
    # print(attendees)
    for row in attendees:
        print(row.Member.name)


add_attendee('test', 'A A Ron')
