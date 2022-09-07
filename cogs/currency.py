import disnake
import random as rnd
import asyncio

from disnake import Embed
from disnake.ext import commands, tasks
from models.database import Database

HS_ALLOWED_CHANNELS = [1007794808812740729,798935679366594573]
#HS_EMOJI_ID = 799461124248436818
HS_EMOJI_ID = 1015513642478870558
class CurrencyCog(commands.Cog):
    def __init__(self, bot) -> None:
        self.bot: commands.InteractionBot = bot
        self.db = Database()
        self.last_person_broke = None
        self.start_hs_random_message_task.start()
        self.cooldowns = {}

    @tasks.loop(count=1)
    async def start_hs_random_message_task(self) -> None:
        await self.bot.wait_for('ready')
        self.HS_EMOJI = self.bot.get_emoji(HS_EMOJI_ID)
        await self.start_random_message_sender()

    
    @commands.slash_command()
    async def hs_leaderboard(
        self,
        ctx: disnake.ApplicationCommandInteraction) -> None:
        """
        How do you compare to the other users?
        """
        users = self.db.hs_get_all()

        users = sorted(users, key=lambda u: u[1], reverse=True)
        ldr_brd = ""
        counter = 1
        for u in users:
            ldr_brd += f"{counter}: <@{u[0]}> - {self.HS_EMOJI}**{u[1]}**\n"
            counter += 1
        await ctx.send(embed=Embed(description=ldr_brd))


    @commands.slash_command()
    async def hs_points(
        self,
        ctx: disnake.ApplicationCommandInteraction):
        """
        How many HS! points you have 
        """
        await ctx.send(embed=Embed(description=f"{self.HS_EMOJI}{self.db.hs_get_points(ctx.author.id)}"), ephemeral=True)
    
    
    @commands.slash_command()
    async def hs_collect(
        self,
        ctx: disnake.ApplicationCommandInteraction) -> None:
        """
        Need a handout? Take 5 HS! points on the house.
        """
        if self.db.hs_get_points(ctx.author.id) > 0: 
            await ctx.send(embed=Embed(description="You aren't broke yet!"),ephemeral=True)
            return

        if self.last_person_broke == ctx.author:
            await ctx.send(embed=disnake.Embed(description=f"One of those days... take +{self.HS_EMOJI}10"),ephemeral=True)
            self.db.hs_add_points(ctx.author.id, 20)
        else:
            self.last_person_broke = ctx.author
            self.db.hs_add_points(ctx.author.id, 10)
            await self.hs_points(ctx)


    @commands.slash_command()
    async def hs_gamble(
        self,
        ctx: disnake.ApplicationCommandInteraction,
        amount: int,
        multiplier: int = 2) -> None:
        """
        Gamble some HS! points to win big! Odds are 1/(multiplier*2)...default is (1/4)

        Parameters
        ----------
        amount: :class:`int`
            The amount to gamble
        multiplier: :class:`int`
            (amount * mult) is your reward. Higher the multiplier the less odds!
        """
        if multiplier < 2:
            await ctx.send(embed=Embed(description="To gamble you need a multiplier of at least 2!"), ephemeral=True)
            return

        if not await self.hs_sub_points(ctx,amount): return

        reward = (amount*multiplier) if 1 == rnd.randint(1,multiplier*2) else 0

        points = self.db.hs_add_points(ctx.author.id, reward)
        
        if reward > 0:
            await ctx.send(embed=Embed(description=f"{ctx.author.mention} gambles {self.HS_EMOJI}**{amount}** and wins {self.HS_EMOJI}**{reward}**! ({self.HS_EMOJI}{points})"))
        else:
            await ctx.send(embed=Embed(description=f"{ctx.author.mention} gambles {self.HS_EMOJI}**{amount}** away.... ({self.HS_EMOJI}{points})"))


    @commands.slash_command()
    async def hs_double(
        self,
        ctx: disnake.ApplicationCommandInteraction) -> None:
        """
        50/50 to lose all your points or double your points...
        """
        points = self.db.hs_get_points(ctx.author.id)

        if not points > 0:
            await ctx.send(embed=Embed(description="Can't double nothing... try `/hs_collect`"),ephemeral=True)
            return

        reward = points if 1 == rnd.randint(1,2) else 0

        points = self.db.hs_add_points(ctx.author.id, reward)
        
        if reward > 0:
            await ctx.send(embed=Embed(description=f"{ctx.author.mention} took a chance and now has {self.HS_EMOJI}**{points}**!"))
        else:
            self.db.hs_sub_points(ctx.author.id,points)
            await ctx.send(embed=Embed(description=f"{ctx.author.mention} took a chance and lost {self.HS_EMOJI}**{points}** :("))

        
    @commands.slash_command()
    async def hs_dice(
        self,
        ctx: disnake.ApplicationCommandInteraction,
        amount: int,
        guess: commands.Range[1,6]) -> None:
        """
        Rolls 6 dice. Payout = dice*bet

        Parameters
        ----------
        amount: :class:`int`
            The amount of HS! points to bet
        guess: :class:`int`
            The number to guess
        """

        if not await self.hs_sub_points(ctx, amount): return            

        rolls = [str(self.roll_dice()) for x in range(6)]

        payout = rolls.count(str(guess))*amount
        points = self.db.hs_add_points(ctx.author.id, payout)

        if payout > 0:
            await ctx.send(embed=disnake.Embed(description=f"You bet **{amount}**\nYou guess **{guess}**.\nYou rolled {','.join(rolls)}\n\nYou win {self.HS_EMOJI}**{payout}**! ({self.HS_EMOJI}{points})"))
        else:
            await ctx.send(embed=disnake.Embed(description=f"You bet **{amount}**\nYou guess **{guess}**.\nYou rolled {','.join(rolls)}\n\nYou gambled away {self.HS_EMOJI}**{amount}**... ({self.HS_EMOJI}{points})"))

    @commands.slash_command()
    async def hs_lottery_info(
        self,
        ctx: disnake.ApplicationCommandInteraction) -> None:
        """
        Info about HS! Lottery minigame
        """

        info = f"""
        Current Jackpot: {self.HS_EMOJI}{self.db.hs_get_lotto_jackpot()}
        Costs 5 HS! points to play.

        The bot then simulates a lottery ticket and the winning numbers. 
        Payout is a percentage of the jackpot determined on how many numbers match.
        Regular numbers are picked [1,15] and the special number is picked [1,5]

        Matches = (Regular Number, Special Number) -> (5,1) is jackpot

        Result - payout - odds
        (0,1)  - 0.01%   - 1 in 5
        (1,1)  - 0.2%   - 1 in 75
        (2,1)  - 0.8%   - 1 in 455
        (3,0)  - 1.0%   - 1 in 525
        (4,0)  - 1.5%   - 1 in 1,365
        (3,1)  - 3.0%  - 1 in 2,275
        (5,0)  - 5.0%  - 1 in 3,003
        (4,1)  - 10.0%  - 1 in 6,825
        (5,1)  - 100.%  - 1 in 15,015

        Jackpot is increased by 1% everytime someone plays. 
        """
        await ctx.send(embed=Embed(description=info))

    @commands.slash_command()
    async def hs_lottery(
        self,
        ctx: disnake.ApplicationCommandInteraction) -> None:
        """
        Simulate a lottery ticket, costs 5 HS! points. Entries add 100 to jackpot
        """

        await ctx.response.defer()

        jackpot = self.db.hs_get_lotto_jackpot()
        if not jackpot:
            await ctx.send("No jackpot set yet")
            return

        if not await self.hs_sub_points(ctx, 5): return         

        lotto_range = range(1,16)
        ball_range = range(1,6)

        user_numbers = sorted(rnd.sample(lotto_range,5))
        user_ball = rnd.choice(ball_range)
        lotto_numbers = sorted(rnd.sample(lotto_range,5))
        lotto_ball = rnd.choice(ball_range)
        white_matches = len(set(user_numbers).intersection(set(lotto_numbers)))
        ball_match = 1 if lotto_ball == user_ball else 0

        winning_tuple = (white_matches, ball_match)
        payout = 0

        # 1 ball (1/5)
        if winning_tuple == (0,1):
            payout = round(jackpot*0.0001)
        # 1 num and 1 ball (1/75)
        elif winning_tuple == (1,1):
            payout = round(jackpot*0.002)
        # 3 num (1/455)
        elif winning_tuple == (3,0):
            payout = round(jackpot*0.008)
        # 2 num and 1 ball (1/525)
        elif winning_tuple == (2,1):
            payout = round(jackpot*0.01)
        # 4 num (1/1,365)
        elif winning_tuple == (4,0):
            payout = round(jackpot*0.015)
        # 3 num and 1 ball (1/2,275)
        elif winning_tuple == (3,1):
            payout = round(jackpot*0.03)
        # 5 num (1/3,003)
        elif winning_tuple == (5,0):
            payout = round(jackpot*0.05)
        # 4 num and 1 ball (1/6,825)
        elif winning_tuple == (4,1):
            payout = round(jackpot*0.10)
        # jackpot (1/15,015)
        elif winning_tuple == (5,1):
            payout = jackpot
        
        points = self.db.hs_add_points(ctx.author.id, payout)
        master_str = f"""
        You: **{",".join([str(x) for x in user_numbers])}** [**{user_ball}**]
        Lottery: **{",".join([str(x) for x in lotto_numbers])}** [**{lotto_ball}**]
        Matches: {winning_tuple}

        You win:{self.HS_EMOJI}**{payout}**\t({self.HS_EMOJI}{points})
        """
        # hit jackpot
        if payout == jackpot:
            self.db.hs_update_lotto_jackpot(5000)
            await ctx.edit_original_message(embed=Embed(description=master_str+f"\n\nYOU HIT THE JACKPOT OF {self.HS_EMOJI}**{payout}**!!!! ({self.HS_EMOJI}{points})"))
            return

        jackpot -= payout
        jackpot = round((jackpot*1.01))
        self.db.hs_update_lotto_jackpot(jackpot)
        master_str += f"\nJackpot is now {self.HS_EMOJI}**{jackpot}**"
        await ctx.edit_original_message(embed=Embed(description=master_str))
        

    ### UTIL ###
    
    def roll_dice(self):
        return rnd.randint(1,6)

    async def start_random_message_sender(self) -> None:
        """ After X amount of time send a random message that the user can react on to get HS! points """

        time_before_next_message = rnd.randint(1800,21600)
        print(f"Next random message in {time_before_next_message} seconds.")
        await asyncio.sleep(time_before_next_message)

        channel: disnake.TextChannel = self.bot.get_channel(rnd.choice(HS_ALLOWED_CHANNELS))

        hs_msg = await channel.send(embed=Embed(description=f"A wild {self.HS_EMOJI} has appeared! First to react gets {self.HS_EMOJI}**25**!"))
        await hs_msg.add_reaction(self.HS_EMOJI)

        def hs_check(reaction: disnake.Reaction, user: disnake.User):
            return reaction.emoji == self.HS_EMOJI and reaction.message == hs_msg and user.id != self.bot.user.id

        reaction, r_user = await self.bot.wait_for('reaction_add', check=hs_check)
        self.db.hs_add_points(r_user.id,25)
        await hs_msg.delete()
        await self.start_random_message_sender()


    async def hs_sub_points(self, ctx: disnake.ApplicationCommandInteraction, amount: int):
        """ Checks if user has enough points for specified store item and subtracts or tells them they don't have enough """
        points = self.db.hs_get_points(ctx.author.id)
        if points >= amount:
            self.db.hs_sub_points(ctx.author.id, amount)
            return True
        else:
            await ctx.send(embed=Embed(description=f"You don't have enough {self.HS_EMOJI}!"), ephemeral=True)
            return False

def setup(bot):
    bot.add_cog(CurrencyCog(bot))