import disnake
import os
import openai
import shutil
import requests
import unicodedata
import re
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
        if not os.path.exists("dalle_pics"):
            os.makedirs("dalle_pics")

        with open(f"dalle_pics/{self.slugify(prompt)}.png",'wb') as f:
            shutil.copyfileobj(res.raw,f)

        img = disnake.File("temp_dalle.png")
        await ctx.send(file=img)

    def slugify(self, value, allow_unicode=False):
        """
        Taken from https://github.com/django/django/blob/master/django/utils/text.py
        Convert to ASCII if 'allow_unicode' is False. Convert spaces or repeated
        dashes to single dashes. Remove characters that aren't alphanumerics,
        underscores, or hyphens. Convert to lowercase. Also strip leading and
        trailing whitespace, dashes, and underscores.
        """
        value = str(value)
        if allow_unicode:
            value = unicodedata.normalize('NFKC', value)
        else:
            value = unicodedata.normalize('NFKD', value).encode('ascii', 'ignore').decode('ascii')
        value = re.sub(r'[^\w\s-]', '', value.lower())
        return re.sub(r'[-\s]+', '-', value).strip('-_')

def setup(bot):
    bot.add_cog(DalleCog(bot))