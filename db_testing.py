from pprint import pprint
from sqlalchemy import engine, create_engine
from sqlalchemy.orm import sessionmaker
from models import Base, Event, Member, Attendance
from random import randint

# Database Connection
engine = create_engine('sqlite:///event-bot.db', echo=False)
Session = sessionmaker(bind=engine)
session = Session()

global event_list

event_list = []

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
    # print(event.id)
    # Number of people attending
    attending = session.query(Attendance).filter(Attendance.event_id == event.id).count()
    attendees = session.query(Attendance.member_id).join(Member, Member.id == Attendance.member_id)
    print(attendees)
    for row in attendees:
        print(row.member_id)


def record_attendance(event_id: int, member: int, attendance: str) -> None:
    """
    event_id: The ID of the event, this is associated with the message id number
    member: The ID of the member from discord
    attendance: The attendance of the member, yes, maybe, no
    return: None
    TODO: Send message to member,
        check if event_id exists to weed out reactions to other messages,
        update if member changes mind
    """
    attending = Attendance(member_id=member, event_id=event_id, attendance=attendance)
    session.add(attending)
    session.commit()

# add_attendee('test', 'A A Ron')
print_attendees("test_event3")
# exist = session.query(session.query(Attendance).filter(Attendance.member_id == 123).exists()).scalar()
# print(exist)

