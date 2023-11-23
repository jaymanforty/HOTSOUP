import os
import disnake
import logging
import datetime

from os.path import exists
from disnake.ext import commands
from dotenv import load_dotenv

from db.config import engine, Base

load_dotenv()
logging.basicConfig(format='%(asctime)s %(message)s',datefmt="%m/%d/%Y %I:%M:%S %p",level=logging.INFO)

description = """Wow I'm a description!"""

intents = disnake.Intents.default()
intents.members = True
intents.message_content = True

commands_sync_flags = commands.CommandSyncFlags(sync_commands=True)

# Gets the test guild if supplied in .env file
# Commands will be registered as global commands if no test guild
test_guild = os.getenv('TEST_GUILD')
test_guild = [int(test_guild)] if test_guild else None

#Define the bot
bot = commands.InteractionBot(
    intents = intents,
    test_guilds = test_guild,
    command_sync_flags=commands_sync_flags
)

#Load the cogs into the bot from the directory
for c in os.listdir("cogs"):
    if c.endswith(".py"):
        bot.load_extension("cogs."+c[:-3])

#log command
@bot.event
async def on_slash_command(ctx:disnake.ApplicationCommandInteraction):
    logging.info(f" Command: {ctx.application_command.name} - User: {ctx.author.id}|{ctx.author.name}#{ctx.author.discriminator}")


#on_ready event
@bot.event
async def on_ready():

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        bot.dispatch('db_ready')
        logging.info('Database initialized')

    print(f'Logged in as {bot.user} (ID: {bot.user.id})')
    print( '-------------------------------------------')


#Starts the bot
bot.run(os.getenv('DISCORD_TOKEN'))