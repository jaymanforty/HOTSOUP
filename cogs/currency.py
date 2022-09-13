import disnake
import random as rnd
import asyncio

from disnake import Embed
from disnake.ext import commands, tasks
from models.database import Database

HS_ALLOWED_CHANNELS = [1007794808812740729,798935679366594573]
#HS_EMOJI_ID = 799461124248436818
HS_EMOJI_ID = 1015513642478870558
LOTTERY_COST = 5

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
        amount: commands.Range[1,100],
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
        amount: commands.Range[1,50],
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
        Costs 10 HS! points to play per ticket

        The bot then simulates however many lottery tickets [1,10] you decide. 
        Payout is determined on how many numbers match.
        Regular numbers are picked [1,15] and the special number is picked [1,10]

        Matches = (Regular Number, Special Number) -> (5,1) is jackpot
        ```
        Result - payout - odds
        (0,1)  - 5        - 1 in 10
        (1,1)  - 5        - 1 in 150
        (2,1)  - 10       - 1 in 910
        (3,0)  - 10       - 1 in 1,050
        (4,0)  - 100      - 1 in 2,730
        (3,1)  - 100      - 1 in 4,550
        (5,0)  - 1000     - 1 in 6,006
        (4,1)  - 2500     - 1 in 13,650
        (5,1)  - jackpot  - 1 in 30,030
        ```
        Jackpot is increased by 5 every ticket with a default of 5000. 
        Also due to my laziness in coding, if multiple tickets win jackpot they'll all be awarded the jackpot
        """
        await ctx.send(embed=Embed(description=info))
 
    @commands.slash_command()
    async def hs_lottery(
        self,
        ctx: disnake.ApplicationCommandInteraction,
        plays: commands.Range[1,10] = 1) -> None:
        """
        Simulate a lottery ticket, costs 5 HS! points. Entries add 5 for every ticket to jackpot
        """
        await ctx.response.defer()

        jackpot = self.db.hs_get_lotto_jackpot()
        if not jackpot:
            await ctx.send("No jackpot set yet")
            return

        if not await self.hs_sub_points(ctx, LOTTERY_COST*plays): return         

        lotto_range = range(1,16)
        ball_range = range(1,11)

        
        lotto_numbers = sorted(rnd.sample(lotto_range,5))
        lotto_ball = rnd.choice(ball_range)

        lotto = {"user_tickets": {}, "lotto_nums":lotto_numbers,"lotto_ball":lotto_ball}
        for i in range(0,plays):
            lotto["user_tickets"][i] = {"nums": sorted(rnd.sample(lotto_range,5)), "ball":rnd.choice(ball_range)}

        
        lotto = self.do_lotto_matches(lotto)
        winnings = self.get_lotto_winnings(lotto)
        points = self.db.hs_add_points(ctx.author.id, winnings)

        ticket_str = self.get_lotto_ticket_str(points, winnings, lotto)
        
        await ctx.send(embed=Embed(description=ticket_str))
        

    ### UTIL ###
    def get_lotto_ticket_str(self, total_points: int, winnings: int, lotto: dict) -> str:
        """ Returns a formatted string displaying ticket info """
        user_tickets = lotto["user_tickets"]
        master_str = f"""
        **Winning Numbers**
        `{",".join([str(i).zfill(2) for i in lotto["lotto_nums"]])} [{lotto["lotto_ball"]}]`

        **Your Numbers**
        ```{"{0}".join([self._get_lotto_ticket_str(user_tickets[t]) for t in user_tickets])}```

        **Net Winnings**
        {self.HS_EMOJI}**{winnings-(len(user_tickets)*LOTTERY_COST):+}** | {self.HS_EMOJI}{total_points}

        Jackpot is now {self.HS_EMOJI}**{self.db.hs_get_lotto_jackpot()}**""".format("\n")
        return master_str


    def _get_lotto_ticket_str(self, ticket: dict) -> str:
        """ Returns a single line string for the ticket """
        return f"{','.join([str(i).zfill(2) for i in ticket['nums']])} [{ticket['ball']}] - {ticket['winning_tuple']} - {ticket['payout']}"


    def get_lotto_winnings(self, lotto: dict) -> int:
        jackpot = self.db.hs_get_lotto_jackpot()
        winnings = 0
        for t in lotto["user_tickets"]:
            winnings += lotto["user_tickets"][t]["payout"]
            if lotto["user_tickets"][t]["payout"] >= jackpot:
                self.db.hs_update_lotto_jackpot(10000)

        self.db.hs_update_lotto_jackpot(jackpot + ((t+1)*LOTTERY_COST))
        return winnings



    def do_lotto_matches(self, lotto: dict) -> dict:
        """ Returns a dict with added properties to ticket dicts doing winning tuple and payout """
        jackpot = self.db.hs_get_lotto_jackpot()
        for t in lotto["user_tickets"]:

            user_nums = lotto["user_tickets"][t]["nums"]
            user_ball = lotto["user_tickets"][t]["ball"]

            white_matches = len(set(user_nums).intersection(set(lotto["lotto_nums"])))
            ball_match = 1 if lotto["lotto_ball"] == user_ball else 0
            winning_tuple = (white_matches, ball_match)
            payout = 0
            # 1 ball (1/10)
            if winning_tuple == (0,1):
                payout = 5
            # 1 num and 1 ball (1/150)
            elif winning_tuple == (1,1):
                payout = 5
            # 3 num (1/910)
            elif winning_tuple == (3,0):
                payout = 10
            # 2 num and 1 ball (1/1050)
            elif winning_tuple == (2,1):
                payout = 10
            # 4 num (1/2730)
            elif winning_tuple == (4,0):
                payout = 100
            # 3 num and 1 ball (1/4550)
            elif winning_tuple == (3,1):
                payout = 200
            # 5 num (1/6006)
            elif winning_tuple == (5,0):
                payout = 1000
            # 4 num and 1 ball (1/13650)
            elif winning_tuple == (4,1):
                payout = 2500
            # jackpot (1/30030)
            elif winning_tuple == (5,1):
                payout = jackpot
            
            lotto["user_tickets"][t]["winning_tuple"] = winning_tuple
            lotto["user_tickets"][t]["payout"] = payout

        return lotto

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