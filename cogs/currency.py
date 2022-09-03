import disnake
import random as rnd
import asyncio

from disnake import Embed
from disnake.ext import commands, tasks
from models.database import Database

HS_ALLOWED_CHANNELS = [1007794808812740729,798935679366594573]
HS_EMOJI_ID = 799461124248436818
class CurrencyCog(commands.Cog):
    def __init__(self, bot) -> None:
        self.bot: commands.InteractionBot = bot
        self.db = Database()
        self.start_hs_random_message_task.start()

    @tasks.loop(count=1)
    async def start_hs_random_message_task(self) -> None:
        await self.bot.wait_for('ready')
        self.HS_EMOJI = self.bot.get_emoji(HS_EMOJI_ID)
        await self.start_random_message_sender()

    
    @commands.slash_command()
    async def hs_leaderboard(
        self,
        ctx: disnake.ApplicationCommandInteraction) -> None:
        """
        How do you compare to the other users?
        """
        users = self.db.hs_get_all()

        users = sorted(users, key=lambda u: u[1], reverse=True)
        ldr_brd = ""
        counter = 1
        for u in users:
            ldr_brd += f"{counter}: <@{u[0]}> - {self.HS_EMOJI}**{u[1]}**\n"
            counter += 1
        await ctx.send(embed=Embed(description=ldr_brd))


    @commands.slash_command()
    async def hs_points(
        self,
        ctx: disnake.ApplicationCommandInteraction):
        """
        How many HS! points you have 
        """
        await ctx.send(embed=Embed(description=f"{self.HS_EMOJI}{self.db.hs_get_points(ctx.author.id)}"), ephemeral=True)
    
    
    @commands.slash_command()
    async def hs_collect(
        self,
        ctx: disnake.ApplicationCommandInteraction) -> None:
        """
        Need a handout? Take 5 HS! points on the house.
        """
        if self.db.hs_get_points(ctx.author.id) > 0: 
            await ctx.send(embed=Embed(description="You aren't broke yet!"),ephemeral=True)
            return
        self.db.hs_add_points(ctx.author.id, 5)
        await self.hs_points(ctx)


    @commands.slash_command()
    async def hs_gamble(
        self,
        ctx: disnake.ApplicationCommandInteraction,
        amount: int,
        multiplier: int = 2) -> None:
        """
        Gamble some HS! points to win big! Odds are 1/(multiplier*2)

        Parameters
        ----------
        amount: :class:`int`
            The amount to gamble
        multiplier: :class:`int`
            (amount * mult) is your reward. Higher the multiplier the less odds!
        """
        if multiplier == 1:
            await ctx.send(embed=Embed(description="To gamble you need a multiplier of at least 2!"), ephemeral=True)
            return

        if not await self.hs_sub_points(ctx,amount): return

        reward = (amount*multiplier) if 1 == rnd.randint(1,multiplier*2) else 0

        points = self.db.hs_add_points(ctx.author.id, reward)
        
        if reward > 0:
            await ctx.send(embed=Embed(description=f"{ctx.author.mention} gambles {self.HS_EMOJI}**{amount}** and wins {self.HS_EMOJI}**{reward}**! ({self.HS_EMOJI}{points})"))
        else:
            await ctx.send(embed=Embed(description=f"{ctx.author.mention} gambles {self.HS_EMOJI}**{amount}** away.... ({self.HS_EMOJI}{points})"))


    @commands.slash_command()
    async def hs_double(
        self,
        ctx: disnake.ApplicationCommandInteraction) -> None:
        """
        50/50 to lose all your points or double your points...
        """
        points = self.db.hs_get_points(ctx.author.id)

        if not points > 0:
            await ctx.send(embed=Embed(description="Can't double nothing... try `/hs_collect`"),ephemeral=True)
            return

        reward = points if 1 == rnd.randint(1,2) else 0

        points = self.db.hs_add_points(ctx.author.id, reward)
        
        if reward > 0:
            await ctx.send(embed=Embed(description=f"{ctx.author.mention} took a chance and now has {self.HS_EMOJI}**{points}**!"))
        else:
            self.db.hs_sub_points(ctx.author.id,points)
            await ctx.send(embed=Embed(description=f"{ctx.author.mention} took a chance and lost {self.HS_EMOJI}**{points}** :("))

  
    ### UTIL ###

    async def start_random_message_sender(self) -> None:
        """ After X amount of time send a random message that the user can react on to get HS! points """

        time_before_next_message = rnd.randint(1800,21600)
        print(f"Next random message in {time_before_next_message} seconds.")
        await asyncio.sleep(time_before_next_message)

        channel: disnake.TextChannel = self.bot.get_channel(rnd.choice(HS_ALLOWED_CHANNELS))

        hs_msg = await channel.send(embed=Embed(description=f"A wild {self.HS_EMOJI} has appeared! First to react gets {self.HS_EMOJI}**25**!"))
        await hs_msg.add_reaction(self.HS_EMOJI)

        def hs_check(reaction: disnake.Reaction, user: disnake.User):
            return reaction.emoji == self.HS_EMOJI and reaction.message == hs_msg and user.id != self.bot.user.id

        reaction, r_user = await self.bot.wait_for('reaction_add', check=hs_check)
        self.db.hs_add_points(r_user.id,25)
        await hs_msg.delete()
        await self.start_random_message_sender()


    async def hs_sub_points(self, ctx: disnake.ApplicationCommandInteraction, amount: int):
        """ Checks if user has enough points for specified store item and subtracts or tells them they don't have enough """
        points = self.db.hs_get_points(ctx.author.id)
        if points >= amount:
            self.db.hs_sub_points(ctx.author.id, amount)
            return True
        else:
            await ctx.send(embed=Embed(description=f"You don't have enough {self.HS_EMOJI}!"), ephemeral=True)
            return False

def setup(bot):
    bot.add_cog(CurrencyCog(bot))