import disnake
import random as rnd
from disnake.ext import commands


class DovesCog(commands.Cog):
    def __init__(self, bot) -> None:
        self.bot: commands.InteractionBot = bot
        self.mute_doves_users = set()

    @commands.slash_command()
    async def only_doves_can_use_this(
        self,
        ctx: disnake.ApplicationCommandInteraction,
        user: disnake.Member) -> None:
        """
        Mute whoever has muted you
        """
        if ctx.author.id != 452655064989958164:
            await ctx.send("Nice try", ephemeral=True)
            return
        if user.id == 452655064989958164 or user.id not in self.mute_doves_users:
            await ctx.send("Nice try bird",ephemeral=True)
            return
        s = rnd.randint(150,300)
        await ctx.guild.timeout(user,duration=s)
        await ctx.send(f"Muted {user.display_name} for {s} seconds")
        self.mute_doves_users.remove(user.id)

    @commands.slash_command()
    @commands.cooldown(1,86400, commands.BucketType.member)
    async def mute_doves(
        self,
        ctx: disnake.ApplicationCommandInteraction) -> None:
        """
        Mute doves for being cringe, but careful that means he can mute you too!
        """
        if ctx.author.id == 452655064989958164:
            await ctx.send("Nice try bird", ephemeral=True)
            return

        m = ctx.guild.get_member(452655064989958164)
        s = rnd.randint(1,300)
        await ctx.guild.timeout(m,duration=s)
        await ctx.send(f"Muted doves for {s} seconds")
        self.mute_doves_users.add(ctx.author.id)

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