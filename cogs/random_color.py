from colorsys import hls_to_rgb, rgb_to_hls
import disnake
import random as rnd
import time

from PIL import Image
from disnake.ext import commands

class RandomColor(commands.Cog):
    def __init__(self, bot) -> None:
        self.bot: commands.InteractionBot = bot
        self.cooldowns = {}

    # Automatically create and assign a new role of the persons name with custom
    '''
    @commands.slash_command()
    @commands.cooldown(1,86400)
    async def random_name_color(
        self,
        ctx: disnake.ApplicationCommandInteraction) -> None:
        """
        Change your name color, can use once per day.
        """
        rgb = tuple(self.random_rgb())
        hexcode = self.rgb_to_hex(rgb)
        color_int = int(hexcode, 16)

        if ctx.author.name not in [x.name for x in ctx.guild.roles]:
            r = await ctx.guild.create_role(name=ctx.author.name, color=color_int)
            print(r.position)
            await r.edit(position=ctx.guild.roles[-1].position-1) #always top level so their name changes color
            await ctx.author.add_roles(r)
        else:
            r = [x for x in ctx.guild.roles if ctx.author.name in x.name][0]
            await r.edit(color=color_int)
            await ctx.author.add_roles(r)

        await ctx.send(embed=disnake.Embed(description=f"Changed name color to #**{hexcode.upper()}**", color=color_int), ephemeral=True)
    '''

    @commands.slash_command()
    @commands.cooldown(1,86400, commands.BucketType.member)
    async def doves(
        self,
        ctx: disnake.ApplicationCommandInteraction) -> None:
        """
        Change Dove's name color, can use once per day.
        """
        rgb = tuple(self.random_rgb())
        hexcode = self.rgb_to_hex(rgb)
        color_int = int(hexcode, 16)
        m = ctx.guild.get_member(149255092124647424)

        try:
            r = [x for x in ctx.guild.roles if "circles308" in x.name][0]
            await r.edit(color=color_int)
            await m.add_roles(r)
        except IndexError:
            await ctx.send("He doesn't have the role anymore! :( ", ephemeral=True)
            return

        await ctx.send(embed=disnake.Embed(description=f"Changed name color to #**{hexcode.upper()}**", color=color_int), ephemeral=True)
    

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