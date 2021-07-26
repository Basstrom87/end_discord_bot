import discord
import tokens
from discord.ext import commands
from sqlalchemy import engine, create_engine
from sqlalchemy.orm import sessionmaker
from datetime import datetime
from models import Base, Event, Member, Attendance
from tabulate import tabulate

# Database Connection
engine = create_engine('sqlite:///event-bot.db', echo=False)
Session = sessionmaker(bind=engine)
session = Session()
# If table doesn't exist, Create the database
if not engine.dialect.has_table(engine.connect(), 'event'):
    Base.metadata.create_all(engine)

# Bot information
description = 'Basstrom87s Dev Bot'
bot = commands.Bot(command_prefix='?', description=description)
token = tokens.bot_token


@bot.event
async def on_ready():
    print(bot.user.id)
    print(bot.user.name)
    print('---------------')
    print('This bot is ready for action!')


@bot.command(pass_context=True)
async def ping(ctx):
    '''Returns pong when called'''
    author = ctx.message.author.name
    server = ctx.message.guild.name
    # Send message to user
    # await ctx.message.author.send(f'Pong for {author} from {server}!')

    # Send reply to message in chat
    await ctx.send(f'Pong for {author} from {server}!')


@bot.command(pass_context=True)
async def create(ctx, name: str, date: str, time: str='0:00am'):
    '''Creates an event with specified name and date
        example: ?create party 01/12/2021 13:40
    '''
    server = ctx.message.guild.name
    date_time = '{} {}'.format(date, time)
    try:
        event_date = datetime.strptime(date_time, '%d/%m/%Y %H:%M:%S')
        event = Event(name=name, server=server, date=event_date)
        session.add(event)
        session.commit()
        await ctx.send(f'Event {name} created successfully for {event.date}')
    except Exception as e:
        await ctx.send('Could not complete your command')
        print(e)


@bot.command(pass_context=True)
async def attend(ctx, name: str):
    '''Allows a user to attend an upcoming event
        example: ?attend party
    '''
    author = ctx.message.author.name
    id = ctx.message.author.id

    try:
        count = session.query(Member).filter(Member.id == id).count()
        event = session.query(Event).filter(Event.name == name).first()

        # Verify This event exists
        if not event:
            await ctx.send('This event does not exist')
            return

        # Create member if they do not exist in our database
        if count < 1:
            member = Member(id=id, name=author)
            session.add(member)

        attending = Attendance(member_id=id, event_id=event.id)
        session.add(attending)
        session.commit()
        await ctx.send(f'Member {author} is now attending event {name}')
    except Exception as e:
        await ctx.send('Could not complete your command')
        print(e)


@bot.command()
async def list(ctx):
    '''Displays the list of current events
        example: ?list
    '''
    try:
        events = session.query(Event).order_by(Event.date).all()
        headers = ['Name', 'Date', 'Server']
        rows = [[e.name, e.date, e.server] for e in events]
        table = tabulate(rows, headers)
        await ctx.send('```\n' + table + '```')
    except Exception as e:
        await ctx.send('Could not complete your command')
        print(e)


@bot.command()
async def view(ctx, name: str):
    '''Displays information about a specific event
        example: ?view party
    '''
    try:
        event = session.query(Event).filter(Event.name == name).first()

        # Verify This event exists
        if not event:
            await ctx.send('This event does not exist')
            return

        # Number of people attending
        attending = session.query(Attendance).filter(Attendance.event_id == event.id).count()

        # List of those attending
        attendees_raw = session.query(Member, Attendance)\
            .filter(Member.id == Attendance.member_id)\
            .filter(Attendance.event_id == event.id)\
            .order_by(Member.name.asc())
        attendees = ""
        for row in attendees_raw:
            attendees += "\n" + row.Member.name

        # Put into a list
        info = [['Name', event.name],
                ['Date', event.date],
                ['Server', event.server],
                ['Number Attending', attending],
                ['Attendees', attendees]]
        await ctx.send('```\n' + tabulate(info) + '```')
    except Exception as e:
        await ctx.send('Could not complete your command')
        print(e)


if __name__ == '__main__':
    try:
        bot.run(token)
    except Exception as e:
        print('Could Not Start Bot')
        print(e)
    finally:
        print('Closing Session')
        session.close()