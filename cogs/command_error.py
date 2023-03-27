import logging
import datetime

from disnake.ext import commands
from disnake import Embed, ApplicationCommandInteraction

from exc import CustomCommandError


class CommandErrorCog(commands.Cog):
    def __init__(self, bot: commands.InteractionBot) -> None:
        self.bot = bot


    @commands.Cog.listener()
    async def on_slash_command_error(
        self,
        ctx: ApplicationCommandInteraction,
        error) -> None:
        """
        Listener to handle command errors
        """

        if isinstance(error, commands.errors.CheckFailure):
            await ctx.send(embed=Embed(description="You are not allowed to use this!"), ephemeral=True)

        elif isinstance(error, CustomCommandError):
            await ctx.send(embed=Embed(description=error.message), ephemeral=True)

        elif isinstance(error, commands.errors.CommandOnCooldown):
            hms = str(datetime.timedelta(seconds=round(error.retry_after)))
            hms = f"{hms.split(':')[0]}h:{hms.split(':')[1]}m:{hms.split(':')[2]}s"
            await ctx.send(embed=Embed(description=f"You cannot use this command. Try again in **{hms}**."), ephemeral=True)                   
        else:
            await ctx.send(error)
            logging.error(f"Unhandled Exception from command: {ctx.application_command}", exc_info=error)


def setup(bot):
    bot.add_cog(CommandErrorCog(bot))