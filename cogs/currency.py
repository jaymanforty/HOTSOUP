import random as rnd
import asyncio
from typing import List

import disnake
from disnake import Embed
from disnake.ext import commands, tasks
from sqlalchemy.future import select

from db import DB, async_session, HSPoints
from exc import CustomCommandError
from constants import HS_EMOJI_ID, ALLOWED_CHANNELS

class CurrencyCog(commands.Cog):
    def __init__(self, bot) -> None:
        self.bot: commands.InteractionBot = bot
        self.last_person_broke = None
        self.start_hs_random_message_task.start()
        self.HS_EMOJI = bot.get_emoji(HS_EMOJI_ID)

    @tasks.loop(count=1)
    async def start_hs_random_message_task(self) -> None:
        await self.bot.wait_for('ready')
        self.HS_EMOJI = self.bot.get_emoji(HS_EMOJI_ID)
        await self.start_random_message_sender()

    
    # /leaderboard
    @commands.slash_command()
    async def leaderboard(
        self,
        ctx: disnake.ApplicationCommandInteraction) -> None:
        """
        How do you compare to the other users?
        """
        async with async_session() as session:
            db = DB(session)

            q = await db.db_session.execute(select(HSPoints).order_by(HSPoints.points.desc()))
            all_u: List[HSPoints] = q.scalars().all()

            s = "HS! Points Leaderboard\n\n**User | Total Points | Points Gained | Points Lost**\n\n"

            for i,u in enumerate(all_u):
                s += f"{i+1}: {u.mention} | {self.HS_EMOJI}**{u.points}** | +{u.points_won} | -{u.points_lost}\n"

        await ctx.send(embed=Embed(description=s))

    # /points
    @commands.slash_command()
    async def points(
        self,
        ctx: disnake.ApplicationCommandInteraction):
        """
        How many HS! points you have 
        """
        async with async_session() as session:
            db = DB(session)
            u = await db.get_hs_points_obj(ctx.author.id)
            
            s = f"{u.mention} | {self.HS_EMOJI}**{u.points}** | +{u.points_won} | -{u.points_lost}\n"
            s += f"`/double - Wins: {u.double_wins} | Losses: {u.double_losses}`"

        await ctx.send(embed=Embed(description=s), ephemeral=True)

    # /collect    
    @commands.slash_command()
    async def collect(
        self,
        ctx: disnake.ApplicationCommandInteraction) -> None:
        """
        Need a handout? Take 5 HS! points on the house.
        """
        async with async_session() as session:
            async with session.begin():
                db = DB(session)

                if ctx.author.id == self.last_person_broke:
                    points = 100
                else:
                    points = 50

                self.last_person_broke = ctx.author.id

                try:
                    u = await db.get_hs_points_obj(ctx.author.id)
                except CustomCommandError:
                    u = HSPoints(
                        user_id = ctx.author.id,
                        points = 0,
                        points_won = 0,
                        points_lost = 0,
                        double_wins = 0,
                        double_losses = 0
                    )
                    await db.add(u)

                if u.points > 0:
                    raise CustomCommandError("Cannot collect if you have points already!")
                
                u.points += points

                s = f"You now have {self.HS_EMOJI}{u.points}."

        await ctx.send(embed=Embed(description=s), ephemeral=True)

    # /double
    @commands.slash_command()
    async def double(
        self,
        ctx: disnake.ApplicationCommandInteraction) -> None:
        """
        50/50 to lose all your points or double your points...
        """

        async with async_session() as session:
            async with session.begin():
                db = DB(session)

                u = await db.get_hs_points_obj(ctx.author.id)

                if u.points == 0:
                    raise CustomCommandError("Can't double nothing...")
                
                if rnd.randint(0,1) == 0:
                    u.points_won += u.points
                    s = f"{u.mention} gambled it all and won {self.HS_EMOJI}{u.points}!"
                    u.points *= 2
                    u.double_wins += 1
                else:
                    u.points_lost += u.points
                    s = f"{u.mention} isn't very good at this and lost {self.HS_EMOJI}{u.points}..."
                    u.points = 0
                    u.double_losses += 1

        s += f" ({self.HS_EMOJI}{u.points})"
        await ctx.send(embed=Embed(description=s))

    ############
    ### Util ###
    ############
    async def start_random_message_sender(self) -> None:
        """ After X amount of time send a random message that the user can react on to get HS! points """

        time_before_next_message = rnd.randint(0, 81600)
        print(f"Next random message in {time_before_next_message} seconds.")
        await asyncio.sleep(time_before_next_message)

        channel: disnake.TextChannel = self.bot.get_channel(rnd.choice(ALLOWED_CHANNELS))
        
        #Select random amount of points to award. 25->50->100->500
        random_int = rnd.randint(1,50)
        if random_int < 26:
            points = 25
        elif random_int < 42:
            points = 50
        elif random_int < 50:
            points = 100
        elif random_int < 51:
            points = 500

        hs_msg = await channel.send(embed=Embed(description=f"A wild {self.HS_EMOJI} has appeared! First to react gets {self.HS_EMOJI}**{points}**!"))
        await hs_msg.add_reaction(self.HS_EMOJI)

        def hs_check(reaction: disnake.Reaction, user: disnake.User):
            return reaction.emoji == self.HS_EMOJI and reaction.message == hs_msg and user.id != self.bot.user.id

        reaction, r_user = await self.bot.wait_for('reaction_add', check=hs_check)

        async with async_session() as session:
            async with session.begin():
                db = DB(session)
                try:
                    u = await db.get_hs_points_obj(r_user.id)
                    u.points += points
                except CustomCommandError:
                    u = HSPoints(
                        user_id = r_user.id,
                        points = points,
                        points_won = 0,
                        points_lost = 0,
                        double_wins = 0,
                        double_losses = 0
                    )
                    await db.add(u)
                
        await hs_msg.delete()
        await self.start_random_message_sender()


def setup(bot):
    bot.add_cog(CurrencyCog(bot))