import disnake
import os
import requests
import datetime

from disnake.ext import commands

class APODCod(commands.Cog):

    def __init__(self, bot) -> None:
        self.bot: commands.InteractionBot = bot
        self.api_key = os.getenv("NASA_API_KEY")

    # /apod
    @commands.slash_command()
    async def apod(
        self,
        ctx: disnake.ApplicationCommandInteraction) -> None:
        """
        Displays today's Astronomy Picture of the Day by NASA
        """
        date = datetime.date.today()
        r = requests.get(f'https://api.nasa.gov/planetary/apod?api_key={self.api_key}&date={date}').json()
        embed = disnake.Embed(title=r['title'])

        #sometimes the APOD is a video instead of an HD picture
        if r['media_type'] == "image":
            embed.set_image(url=r['hdurl'])

        embed.url = r['url']

        embed.description = r['explanation']
        embed.set_footer(text=r['date'])
        print(r)
        await ctx.send(embed=embed)

def setup(bot):
    bot.add_cog(APODCod(bot))