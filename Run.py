import os
import disnake
import logging
import datetime

from os.path import exists
from disnake.ext import commands
from dotenv import load_dotenv

from models.database import Database

load_dotenv()
logging.basicConfig(format='%(asctime)s %(message)s',datefmt="%m/%d/%Y %I:%M:%S %p",level=logging.INFO)

#TODO: create local database for bot
db = Database()


description = """Wow I'm a description!"""


intents = disnake.Intents.default()
intents.members = True
intents.message_content = True

commands_sync_flags = commands.CommandSyncFlags(sync_commands=True)

#Define the bot
bot = commands.InteractionBot(
    intents = intents,
    test_guilds = [491700910712684554],
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

#command_error
@bot.event
async def on_slash_command_error(ctx:disnake.ApplicationCommandInteraction, error):
    if isinstance(error, commands.errors.CheckFailure):
        await ctx.send(embed=disnake.Embed(description="You are not allowed to use this"), ephemeral=True)

    elif isinstance(error, commands.errors.CommandOnCooldown):
        await ctx.send(embed=disnake.Embed(description=f"You are on cooldown. Try again after `{str(datetime.timedelta(seconds = round(error.retry_after)))}`"), ephemeral=True)

    else:
        await ctx.channel.send(error)
        logging.error(f"Unhandled Exception from command: {ctx.application_command}", exc_info=error)

    
        

#on_ready event
@bot.event
async def on_ready():
    print(f'Logged in as {bot.user} (ID: {bot.user.id})')
    print( '-------------------------------------------')


#Starts the bot
bot.run(os.getenv('DISCORD_TOKEN'))