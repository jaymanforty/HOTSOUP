import disnake
import random as rnd
from disnake.ext import commands


class DovesCog(commands.Cog):
    def __init__(self, bot) -> None:
        self.bot: commands.InteractionBot = bot

    # /doves
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
        m = ctx.guild.get_member(452655064989958164)

        try:
            r = [x for x in ctx.guild.roles if "circles308" in x.name][0]
            await r.edit(color=color_int)
            await m.add_roles(r)
        except IndexError:
            await ctx.send("He doesn't have the role anymore! :( ", ephemeral=True)
            return

        await ctx.send(embed=disnake.Embed(description=f"Changed name color to #**{hexcode.upper()}**", color=color_int), ephemeral=True)
    
    def random_rgb(self):
        rgb = [rnd.randint(0,255),rnd.randint(0,255),rnd.randint(0,255)]
        rnd.shuffle(rgb)
        return tuple(rgb)

    def rgb_to_hex(self, rgb):
        return '%02x%02x%02x' % rgb
    
def setup(bot):
    bot.add_cog(DovesCog(bot))