import disnake
import asyncio

from random import randint
from disnake.ext import commands
from enum import Enum

class RPSCog(commands.Cog):
    def __init__(self, bot) -> None:
        self.bot: commands.InteractionBot = bot
        self.challenge_message = None

    @commands.slash_command()
    async def rps(
        self,
        ctx: disnake.ApplicationCommandInteraction,
        challengee: disnake.Member,
        rps: str = commands.Param(choices=["🗻", "🧻", "✂"])):

        """
        Rock, Paper, Scissors battle to knock the other out of voice

        Parameters
        ----------
        challengee: :class:`disnake.Member`
            The person you want to challenge
        rps: :class:`str`
            RPS!
        """
        if self.challenge_message:
            await ctx.send("Wait for the current game to finish!", ephemeral=True)
            return

        if not ctx.author.voice or not challengee.voice:
            await ctx.send("Both players need to be in voice chat!", ephemeral=True)
            return

        challenge_message = await ctx.channel.send(challengee.mention,embed=disnake.Embed(description=f"{ctx.author.mention} challenges {challengee.mention} to a game of RPS! Loser gets disconnected from voice."))
        self.challenge_message = challenge_message
        await challenge_message.add_reaction("🗻")
        await challenge_message.add_reaction("🧻")
        await challenge_message.add_reaction("✂")

        await ctx.send("Challenge sent, expires in 60 seconds", ephemeral=True)

        def rps_check(reaction,user):
            return reaction.message == challenge_message and reaction.emoji in ["🗻", "🧻", "✂"] and user == challengee

        # Waits for a reaction of RPS to be added to challenge message. Regardless of what happens first, reaction or timeout, variables are reset
        reaction, user = await self.bot.wait_for('reaction_add', check=rps_check, timeout=60)

        if not reaction or not user:
            self.challenge_message = None
            return
            
        #     | roc | pap | sci
        # roc | -1  |  1  |  0
        # pap |  1  | -1  |  2
        # sci |  0  |  2  | -1

        rps_matrix = [[-1,1,0],[1,-1,2],[0,2,-1]]
        rps_dict = {"🗻": 0, "🧻": 1, "✂": 2}

        winner = rps_matrix[rps_dict[rps]][rps_dict[reaction.emoji]]
        c_choice = rps_dict[rps]
        ce_choice = rps_dict[reaction.emoji]

        await asyncio.sleep(.1*randint(5,15))
        if winner == c_choice:
            await user.edit(voice_channel=None)
        elif winner == ce_choice:
            await ctx.author.edit(voice_channel=None)


        await challenge_message.delete()
        self.challenge_message = None
        


def setup(bot):
    bot.add_cog(RPSCog(bot))