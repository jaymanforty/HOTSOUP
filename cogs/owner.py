import os
import random

from disnake.ext import commands
from disnake import ApplicationCommandInteraction, User, Embed
import openai


from db import async_session, DB, HSPoints
from exc import CustomCommandError
from constants import HS_EMOJI_ID

class OwnerCog(commands.Cog):

    def __init__(self, bot: commands.InteractionBot) -> None:
        self.bot = bot
        openai.api_key = os.getenv("OPENAI_API_KEY")
        self.HS_EMOJI = bot.get_emoji(HS_EMOJI_ID)


    # /setpoints
    @commands.is_owner()
    @commands.slash_command()
    async def setpoints(
            self,
            ctx: ApplicationCommandInteraction,
            user: User,
            points: int) -> None:
        """
        Command to manually set a user's points

        Parameters
        ----------
        user: :class:`User`
            The user to set points of
        points: :class:`int`
            The amount of points to set them to
        """

        async with async_session() as session:
            async with session.begin():
                db = DB(session)

                try:
                    u = await db.get_hs_points_obj(user.id)
                except CustomCommandError:
                    u = HSPoints(
                        user_id = user.id,
                        points = 0,
                        points_won = 0,
                        points_lost = 0,
                        double_wins = 0,
                        double_losses = 0
                    )
                    await db.add(u)

                u.points = points

        await ctx.send(embed=Embed(description=f"Set {user.mention} points to {self.HS_EMOJI}**{u.points}**"), ephemeral=True)

    # /test
    @commands.is_owner()
    @commands.slash_command()
    async def test(
        self,
        ctx: ApplicationCommandInteraction) -> None:

        msgs = await ctx.channel.history(limit=20, oldest_first=False).flatten()

        m_c = [{m.author.name:m.clean_content} for m in msgs if m.content]

        s = ""
        for m in m_c:
            for k in m:
                s += f"{k}: {m[k]}\n"

        s += f"{self.bot.user.name}: "

        r = openai.Completion.create(
            model="text-davinci-003",
            prompt=s,
            max_tokens = 150,
            temperature = random.randint(60,100)/100
            )
        
        response_text = r['choices'][0]['text'].strip()
        estimated_cost = r['usage']['total_tokens'] * (4/1000)
        print("cost ~ ¢", estimated_cost)
        await ctx.send(f"{response_text}", ephemeral=True)



def setup(bot):
    bot.add_cog(OwnerCog(bot))
