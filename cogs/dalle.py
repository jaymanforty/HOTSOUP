import disnake
import os
import openai
import shutil
import requests
from disnake.ext import commands

class DalleCog(commands.Cog):
    def __init__(self,bot) -> None:
        self.bot: commands.InteractionBot = bot
        openai.api_key = os.getenv("OPENAI_API_KEY")


    # /create_image
    @commands.slash_command()
    @commands.cooldown(1,120, commands.BucketType.member)
    async def create_image(
        self,
        ctx: disnake.ApplicationCommandInteraction,
        prompt: str,
        size:str = commands.Param(choices=['1024x1024','512x512','256,256'], default='256x256')) -> None:
        """
        AI generated image

        Parameters
        ----------
        prompt :class:`str`
            The prompt to generate an image with
        size :class:`int`
            1=1024,2=512,3=256
        """

        await ctx.response.defer()
        response = openai.Image.create(prompt=prompt,n=1,size=size)
        image_url = response['data'][0]['url']
        res = requests.get(image_url,stream=True)

        with open(f"dalle_pic.png",'wb') as f:
            shutil.copyfileobj(res.raw,f)
        
        img = disnake.File(f"dalle_pic.png")
        await ctx.send(file=img)

def setup(bot):
    bot.add_cog(DalleCog(bot))