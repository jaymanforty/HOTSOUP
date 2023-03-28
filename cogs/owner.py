import os
import random

from disnake.ext import commands
from disnake import ApplicationCommandInteraction
import openai


from db import async_session, DB


class OwnerCog(commands.Cog):

    def __init__(self, bot: commands.InteractionBot) -> None:
        self.bot = bot
        openai.api_key = os.getenv("OPENAI_API_KEY")


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

        s += "{self.bot.user.name}: "

        r = openai.Completion.create(
            model="text-davinci-003",
            prompt=s,
            max_tokens = 150,
            temperature = random.random()
            )
        
        response_text = r['choices'][0]['text'].strip()
        estimated_cost = r['usage']['total_tokens'] * (4/1000)
        print("cost ~ ¢", estimated_cost)
        await ctx.send(f"{response_text}", ephemeral=True)



def setup(bot):
    bot.add_cog(OwnerCog(bot))
