"""
TODO: Only allow one reaction,
    Message members when they join up to an event with their local time
    Create time button to message members when the event is in their timezone
    Send reminders 24 and 48 hours before an event if they haven't signed up
    Get list of non-responders for an event
    Create repeatability
    Pretty it up

    Future: See how big database can be before performance loss, consider changing to MySQL if this is an issue
"""

from datetime import datetime

import discord
from discord.ext import commands
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from tabulate import tabulate

import tokens
from models import Base, Event, Member, Attendance

# Database Connection
db_engine = create_engine('sqlite:///event-bot.db', echo=False)
Session = sessionmaker(bind=db_engine)
session = Session()
# If table doesn't exist, Create the database
if not db_engine.dialect.has_table(db_engine.connect(), 'event'):
    Base.metadata.create_all(db_engine)

# Bot information
description = 'Basstrom87s Dev Bot'
intents = discord.Intents.default()
intents.members = True
bot = commands.Bot(intents=intents, command_prefix='?', description=description)
token = tokens.bot_token

# Change this to End to be applicable to alliance members only
main_role = "admin"
# Change this to be the TC Channel ID
tc_channel_id = 871586996135530527


@bot.event
async def on_ready():
    print(bot.user.id)
    print(bot.user.name)
    print('---------------')
    print('This bot is ready for action!')


@bot.command()
async def tc_event(ctx):
    # Send message to TC Channel
    channel = bot.get_channel(tc_channel_id)
    embed = discord.Embed(title="TC Event Name Placeholder",
                          description="Upcoming Territory Battle! Sign up Below!",
                          color=0x00458f)
    embed.add_field(name="Time",
                    value="Time placeholder",
                    inline=False)
    embed.add_field(name='Timezone Conversion Link',
                    value='To be url to timezone conversion',
                    inline=False)
    embed.add_field(name='Duration',
                    value='Placeholder for duration',
                    inline=True)
    embed.add_field(name='Repeat',
                    value='Placeholder for repeatability',
                    inline=True)
    message = await channel.send(embed=embed)
    await message.add_reaction('\U00002705')  # Tick
    await message.add_reaction('\U0001F937')  # Shrugging aka Maybe
    await message.add_reaction('\U0000274C')  # Red cross, No


@bot.command(pass_context=True)
async def create(ctx, name: str, date: str, time: str = '0:00am'):
    """Creates an event with specified name and date
        example: ?create party 01/12/2021 13:40
    """
    server = ctx.message.guild.name
    date_time = '{} {}'.format(date, time)
    try:
        event_date = datetime.strptime(date_time, '%d/%m/%Y %H:%M:%S')
        # Check if event exists, if not input the event into the database, id of the event linked to the message id
        if session.query(session.query(Event).filter(Event.date == event_date).exists()).scalar():
            await ctx.send(f"Event {name} Already Exists!")
        else:
            message = await ctx.send(f'Event {name} created successfully for {event_date}')
            await message.add_reaction('\U00002705')  # Tick
            await message.add_reaction('\U0001F937')  # Shrugging aka Maybe
            await message.add_reaction('\U0000274C')  # Red cross, No
            msg_id = message.id
            event = Event(id=msg_id, name=name, server=server, date=event_date)
            session.add(event)
            session.commit()
    except Exception as err:
        await ctx.send('Could not complete your command')
        print(err)


@bot.command(pass_context=True)
async def attend(ctx, name: str):
    """Allows a user to attend an upcoming event
        example: ?attend party
    """
    author = ctx.message.author.name
    auth_id = ctx.message.author.id

    try:
        count = session.query(Member).filter(Member.id == auth_id).count()
        event = session.query(Event).filter(Event.name == name).first()

        # Verify This event exists
        if not event:
            await ctx.send('This event does not exist')
            return

        # Create member if they do not exist in our database
        if count < 1:
            member = Member(id=id, name=author)
            session.add(member)

        # Check to see if person already has marked their attendance
        if session.query(session.query(Attendance).filter(Attendance.member_id == id).exists()).scalar():
            await ctx.send('You have already submitted your attendance for this event, please check other events!')
        else:
            attending = Attendance(member_id=id, event_id=event.id)
            session.add(attending)
            session.commit()
            await ctx.send(f'Member {author} is now attending event {name}')

    except Exception as err:
        await ctx.send('Could not complete your command')
        print(err)


@bot.command()
async def list_events(ctx):
    """Displays the list of current events
        example: ?list
    """
    try:
        events = session.query(Event).order_by(Event.date).all()
        headers = ['Name', 'Date']
        rows = [[event.name, event.date] for event in events]
        table = tabulate(rows, headers)
        await ctx.send('```\n' + table + '```')
    except Exception as err:
        await ctx.send('Could not complete your command')
        print(err)


@bot.command()
async def view_event(ctx, name: str):
    """Displays information about a specific event
        example: ?view party
    """
    try:
        event = session.query(Event).filter(Event.name == name).first()

        # Verify This event exists
        if not event:
            await ctx.send('This event does not exist')
            return

        # Number of people attending
        attending = session.query(Attendance).filter(Attendance.event_id == event.id).count()

        # List of those attending
        attendees_raw = session.query(Member, Attendance) \
            .filter(Member.id == Attendance.member_id) \
            .filter(Attendance.event_id == event.id) \
            .order_by(Member.name.asc())
        print(attendees_raw.all())

        attendees = ""
        for row in attendees_raw.all():
            attendees += "\n" + row.Member.name

        # Put into a list
        info = [['Name', event.name],
                ['Date', event.date],
                ['Number Attending', attending],
                ['Attendees', attendees]]
        await ctx.send('```\n' + tabulate(info) + '```')
    except Exception as err:
        await ctx.send('Could not complete your command')
        print(err)


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


@bot.event
async def on_raw_reaction_add(payload):
    """
    Get when a user presses a reaction button and send it to the database
    """
    # Get username without user code, convert to string and partition it out
    # member_name_str = str(payload.member).partition("#")[0]
    # print(payload.member.bot)
    # Check to see if a real person is reacting to the message
    if not payload.member.bot:
        # Create member if they do not exist in our database
        count = session.query(Member).filter(Member.id == payload.user_id).count()
        if count < 1:
            member = Member(id=payload.user_id, name=str(payload.member).partition("#")[0])
            session.add(member)

        attendance = ""
        if payload.emoji.name == '✅':
            attendance = "Yes"
        elif payload.emoji.name == '🤷':
            attendance = "Maybe"
        elif payload.emoji.name == '❌':
            attendance = "No"
        # print(f"{member_name_str} has responded to the attendance with {attendance}")
        record_attendance(payload.message_id, payload.user_id, attendance)
        print("Record added")


@bot.command(pass_context=True)
@commands.has_any_role('admin', 'leader')
async def update_members(ctx):
    """
    Get a list of all current members that are not bots and have End tag
    Change the main_role variable to suit the main member role, to be changed to End once deployed
    TODO: update members
    """
    member_list = []
    role = discord.utils.find(lambda r: r.name == main_role, ctx.message.guild.roles)
    print(role)
    for member in ctx.guild.members:
        if not member.bot:
            # print(f"{member} has the role of {member.roles}")
            if role in member.roles:
                member_list.append(member.name)
        else:
            pass

    print(member_list)


if __name__ == '__main__':
    try:
        bot.run(token)
    except Exception as e:
        print('Could Not Start Bot')
        print(e)
    finally:
        print('Closing Session')
        session.close()
