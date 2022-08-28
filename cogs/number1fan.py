import disnake
from random import randint
from disnake.ext import commands
from models.database import Database

class Num1FanCog(commands.Cog):
    
    def __init__(self, bot) -> None:
        self.bot: commands.InteractionBot = bot
        self.db = Database()
        self.fan_nums = {1: 981049157978554418, 2: 1013012036625645608, 3: 1013012221514756200}

    @commands.slash_command(
        name="im-a-fan",
        description="Try to be the HOTSOUP! #1 Fan by guessing a number out of 1000."
    )
    async def fan_async(
        self,
        ctx: disnake.ApplicationCommandInteraction,
        guess: int):
        """
        Try to be the HOTSOUP! #1 Fan by guessing a number out of 500.
        If your guess is within 100 = #3 fan, 50 = #2 fan, 0 = #1 fan

        Parameters
        ----------
        guess: :class:`int`
            The number you want to guess with 
        """

        if guess < 1 or guess > 500:
            await ctx.send(embed=disnake.Embed(description="The number can only be [1 -> 500] "), ephemeral=True)
            return
        
        self.db.init_user_guesses(ctx.author.id)

        magic_num = randint(1,500)
        num_guesses = self.db.get_num_guesses(ctx.author.id) + 1

        self.db.update_user_guesses(ctx.author.id, num_guesses)

        #nice
        if "69" in str(guess):
            await self.bot.get_channel(ctx.channel_id).send("nice")

        # assign #1 role
        if abs(guess - magic_num) == 0:    # 1/500   = 0.2%
            await self.update_user_role(ctx.author, 1)
            await ctx.send(embed=disnake.Embed(description=f"{ctx.author.mention} has become **#1** HOTSOUP! Fan.\nTotal Guesses: {num_guesses}"))
            return

        # assign #2 role
        elif abs(guess - magic_num) < 51:  # 100/500 = 20%
            await self.update_user_role(ctx.author, 2)
            await ctx.send(embed=disnake.Embed(description=f"{ctx.author.mention} has become **#2** HOTSOUP! Fan.\nTotal Guesses: {num_guesses}"))
            return

        # assign #3 role
        elif abs(guess - magic_num) < 101: # 200/500 = 40%
            await self.update_user_role(ctx.author, 3)
            await ctx.send(embed=disnake.Embed(description=f"{ctx.author.mention} has become **#3** HOTSOUP! Fan.\nTotal Guesses: {num_guesses}"))
            return

        
        await ctx.send(embed=disnake.Embed(description=f"The number was **{magic_num}**. You were {abs(guess-magic_num)} off. Better luck next time!"), ephemeral=True)


    async def update_user_role(self, user: disnake.Member, num_fan: int):
        """ Updates the role of user to reflect their guess"""
        guild = self.bot.get_guild(user.guild.id)
        previous_owner_id = self.db.get_fan_role_user(num_fan)
        previous_member = guild.get_member(previous_owner_id)

        r = guild.get_role(self.fan_nums[num_fan])
        await user.add_roles(r)

        if not previous_member: return
        await previous_member.remove_roles(r)
        

def setup(bot):
    bot.add_cog(Num1FanCog(bot))