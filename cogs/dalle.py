import disnake
import os
import openai
from disnake.ext import commands

from models.database import Database

class DalleCog(commands.Cog):
    def __init__(self,bot) -> None:
        self.bot: commands.InteractionBot = bot
        self.db = Database()
        openai.api_key = os.getenv("OPENAI_API_KEY")


    @commands.slash_command()
    @commands.cooldown(1,86400, commands.BucketType.member)
    async def create_image(
        self,
        ctx: disnake.ApplicationCommandInteraction,
        prompt: str) -> None:
        """
        AI generated image

        Parameters
        ----------
        prompt :class:`str`
            The prompt to generate an image with
        """
        await ctx.response.defer()
        response = openai.Image.create(prompt=prompt,n=1,size="256x256")
        image_url = response['data'][0]['url']
        await ctx.send(image_url)

def setup(bot):
    bot.add_cog(DalleCog(bot))