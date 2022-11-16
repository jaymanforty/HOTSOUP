import disnake
from disnake.ext import commands,tasks
from models.database import Database

HS_GENERAL = 798935679366594573
TEST_GENERAL = 789593992236236820

class TagCog(commands.Cog):
    def __init__(self, bot) -> None:
        self.bot: commands.InteractionBot = bot
        self.it: disnake.Member = None
        self.notagbacks = None
        self.tag_counter = 0
        self.youreitnerd.start()
        self.db = Database()

    @tasks.loop(hours=1)
    async def youreitnerd(self):
        if self.it:
            await self.bot.get_channel(HS_GENERAL).send(f"{self.it.mention} is it btw, use `/tagyoureit`")
        else:
            if self.tag_counter % 24 == 0:
                await self.bot.get_channel(HS_GENERAL).send(embed=disnake.Embed(description="No one is it... use `/tagyoureit`"))
                self.tag_counter = 0
        self.tag_counter += 1

    @youreitnerd.before_loop
    async def before_youreitnerd(self):
        await self.bot.wait_until_ready()

    @commands.slash_command()
    async def tagyoureit(
        self,
        ctx: disnake.ApplicationCommandInteraction,
        user: disnake.Member) -> None:
        """
        Tag a fellow member of the community as "it"

        Parameters
        -----------
        user :class:`disnake.Member`
            The user to tag
        """
        if ctx.author != self.it and self.it != None:
            await ctx.send(f"{self.it.mention} is it!",ephemeral=True)
            return

        if user == self.notagbacks:
            await ctx.send("No tag backs!",ephemeral=True)
            return

        self.it = user
        self.notagbacks = ctx.author
        count = self.db.hs_add_tag_count(user.id,1)
        await ctx.send(user.mention,embed=disnake.Embed(title=f"Tag you're it!").set_footer(text=f"{count}"))

def setup(bot):
    bot.add_cog(TagCog(bot))