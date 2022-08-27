import disnake
from disnake.ext import commands

class Hello(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self._last_member: disnake.User = None
    
    ### Commands ###

    # /hello
    @commands.slash_command(
        name = "hello",
        description = "Say hello!")
    async def hello_async(
        self,
        ctx: disnake.ApplicationCommandInteraction):

        #log command
        print(f"{ctx.author.name},{ctx.author.id} used slash command Hello")

        if self._last_member == None or self._last_member.id != ctx.author.id:

            await ctx.send(f"Hello {ctx.author.mention}!")
        
        else:

            await ctx.send(f"Hello {ctx.author.mention}! This feels familiar...")
        
        self._last_member = ctx.author


def setup(bot):
    bot.add_cog(Hello(bot))
