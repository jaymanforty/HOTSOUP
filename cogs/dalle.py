import disnake
import os
import openai
import shutil
import requests
from disnake.ext import commands

from models.database import Database

class DalleCog(commands.Cog):
    def __init__(self,bot) -> None:
        self.bot: commands.InteractionBot = bot
        self.db = Database()
        openai.api_key = os.getenv("OPENAI_API_KEY")


    @commands.slash_command()
    @commands.cooldown(1,120, commands.BucketType.member)
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
        response = openai.Image.create(prompt=prompt,n=1,size="1024x1024")
        image_url = response['data'][0]['url']
        res = requests.get(image_url,stream=True)
        with open("temp_dalle.png",'wb') as f:
            shutil.copyfileobj(res.raw,f)
        img = disnake.File("temp_dalle.png")
        await ctx.send(file=img)

def setup(bot):
    bot.add_cog(DalleCog(bot))