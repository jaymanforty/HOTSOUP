from colorsys import hls_to_rgb, rgb_to_hls
import disnake
import random as rnd

from PIL import Image,ImageDraw
from disnake.ext import commands

class RandomColor(commands.Cog):
    def __init__(self, bot) -> None:
        self.bot: commands.InteractionBot = bot

    
    @commands.slash_command()
    async def randomcolor(
        self,
        ctx: disnake.ApplicationCommandInteraction) -> None:
        """
        Generate a random color!
        """

        r,g,b = tuple(self.random_rgb())
        rgb = (r,g,b)

        hexcode = self.rgb_to_hex(rgb)

        img = Image.new('RGB', (100,100), rgb)
        img.save("temp_color.png")
        img = disnake.File("temp_color.png")

        e = disnake.Embed(color=int(hexcode,16))
        e.add_field(name="Hex", value=f"#{hexcode.upper()}")
        e.add_field(name="RGB", value=f"{rgb[0]}, {rgb[1]}, {rgb[2]}")
        e.set_image(file=img)
        await ctx.send(embed=e)

    def get_complimentary_rgb(self, r,g,b):
        h,l,s = rgb_to_hls(r/255,g/255,b/255)
        print(h,l,s)
        h = h+0.5 if h+0.5 < 1.0 else 1-(h+0.5)
        return hls_to_rgb(h,l,s)

    def random_rgb(self):
        rgb = [rnd.randint(0,255),rnd.randint(0,255),rnd.randint(0,255)]
        rnd.shuffle(rgb)
        return tuple(rgb)

    def rgb_to_hex(self, rgb):
        return '%02x%02x%02x' % rgb

def setup(bot):
    bot.add_cog(RandomColor(bot))