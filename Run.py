import os
import disnake
import logging

from os.path import exists
from disnake.ext import commands
from dotenv import load_dotenv

from models.database import Database

load_dotenv()
logging.basicConfig(level=logging.INFO)

#TODO: create local database for bot
db = Database()


description = """Wow I'm a description!"""

intents = disnake.Intents.default()
intents.members = True

#Define the bot
bot = commands.InteractionBot(
    intents = intents,
    descriptions = description,
    test_guilds = [491700910712684554],
    sync_commands = True
)

#Load the cogs into the bot from the directory
for c in os.listdir("cogs"):
    if c.endswith(".py"):
        bot.load_extension("cogs."+c[:-3])

#log command
@bot.event
async def on_slash_command(ctx:disnake.ApplicationCommandInteraction):
    logging.info(f" Command: {ctx.application_command.name} - User: {ctx.author.id}|{ctx.author.display_name}")

#command_error
@bot.event
async def on_slash_command_error(ctx:disnake.ApplicationCommandInteraction, error):
    if isinstance(error, commands.errors.CheckFailure):
        await ctx.send(embed=disnake.Embed(description="You are not allowed to use this"), ephemeral=True)
    else:
        await ctx.send(error)
        logging.error(f"Unhandled Exception from command: {ctx.application_command}", exc_info=error)


#on_ready event
@bot.event
async def on_ready():
    print(f'Logged in as {bot.user} (ID: {bot.user.id})')
    print( '-------------------------------------------')


#Starts the bot
bot.run(os.getenv('DISCORD_TOKEN'))