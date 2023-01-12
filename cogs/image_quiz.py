import disnake
import os
import requests
import openai
import shutil
import random
import json
import re
from difflib import SequenceMatcher
from asyncio.exceptions import TimeoutError
from disnake.ext import commands
from models.database import Database

PROMPTS = [
    "Draw a cartoon of {0}",
    "Draw a comic using {0}",
    "Sketch this: {0}",
    "A photograph of {0}"
] 


class ImageQuizCog(commands.Cog):
    def __init__(self, bot):
        self.bot: commands.InteractionBot = bot
        self.word_api_key = os.getenv("WORDNIK_API_KEY")
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        self.db = Database()
        self.active_games = {}

    @commands.Cog.listener('on_message')
    async def quiz_handler(
        self,
        message: disnake.Message) -> None:
        """
        Look at message and see if it's an answer to any active games
        """
        if message.channel.id not in self.active_games.keys(): return
        word = self.active_games[message.channel.id]
        guess = message.content

        if word.lower() == guess.lower():
            self.bot.dispatch(str(message.channel.id)+"_image_quiz_winner", message)
            return

        if SequenceMatcher(None, guess, word).ratio() > 0.8:
            await message.reply(f"{guess} is close!")

    @commands.slash_command()
    async def play(
        self,
        ctx: disnake.ApplicationCommandInteraction) -> None:
        """
        Play a quiz where you guess the word used to generate the image
        """

        if ctx.channel_id in self.active_games.keys():
            await ctx.send("Game in progress!", ephemeral=True)
            return

        await ctx.response.defer()
        
        init_game_msg = f"Starting Image Quiz!\n\nGenerating a word and an image..."
        e = disnake.Embed(description=init_game_msg)
        
        await ctx.send(embed=e)

        word = await self.get_random_word()

        print("Starting image quiz with word::", word)

        self.active_games[ctx.channel_id] = word
        await self.generate_image(ctx.channel_id)
        
        num_hints = 0
        hint = self.get_hint(word,num_hints)
        e.description = f"**`{hint}`**"
    
        #Build embed with image and hint
        img = disnake.File(f"image_quiz_pics/{ctx.channel_id}.png")
        e.set_image(file=img)
        await ctx.edit_original_message(embed=e)
        
        #give some hints if user isn't guessing correctly
        correct = False
        hinted_word = hint
        while not correct:
            try:
                message: disnake.Message = await self.bot.wait_for(f'{ctx.channel_id}_image_quiz_winner', timeout=30)
                correct = True
            except TimeoutError:
                num_hints += 1
                if num_hints > 3: break #Don't want to make it too easy
                hinted_word = self.get_hint(word,num_hints,hinted_word)
                e.description = f"**`{hinted_word}`**"

                img = disnake.File(f"image_quiz_pics/{ctx.channel_id}.png") #NOTE: Not sure why i have to keep doing this
                e.set_image(file=img)

                await ctx.edit_original_message(embed=e)
    
        if correct:
            #Award whoever guessed it
            total_wins = self.db.get_image_quiz_score(message.author.id) + 1
            self.db.set_image_quiz_score(message.author.id, total_wins)
            await message.reply(f"{message.author.name} has guessed the word! It was **{word}**!\nTotal Wins: **{total_wins}**")
        
        e.description = f"**GAME FINISHED**\n**`{word}`**"
        img = disnake.File(f"image_quiz_pics/{ctx.channel_id}.png")
        e.set_image(file=img)
        await ctx.edit_original_message(embed=e)

        #Remove active games and delete picture file
        self.active_games.pop(ctx.channel_id)
        os.remove(f"image_quiz_pics/{ctx.channel_id}.png")

    @commands.slash_command()
    async def imagequiz_lb(
        self,
        ctx: disnake.ApplicationCommandInteraction) -> None:
        """
        View current leaderboard for Image Quiz!
        """
        await ctx.send("Command under construction👷‍♂️",ephemeral=True)


    ############
    ### UTIL ###
    ############
    def quick_embed(self, description) -> disnake.Embed:
        """ Returns an embed object with specified description """
        e = disnake.Embed(description=description)
        return e

    def get_hint(self, word:str, amount:int, already_hinted:str = None)-> str:
        """ Given a word return a fancy string like ' _ e _ _ o ' for 'hello' """
        #preserve spaces
        spaces = [m.start() for m in re.finditer(' ', word)]
        word = word.replace(' ', '')
        hints = set()

        #if the string is already been parsed for hints find those hints
        if already_hinted:
            [hints.add((l,i)) for i,l in enumerate(already_hinted.replace(' ','')) if l!='_' and l!=' ']

        #choose a random index to use as a hint and add that to our set
        while len(hints) < amount:
            idx = random.randint(0,len(word)-1)
            ltr = word[idx]
            hints.add((ltr,idx)) if idx not in [i[1] for i in hints] else None
            
        hint = list('_'*len(word))
        for h in hints:
            hint[h[1]] = h[0]
        
        #restore spaces
        [hint.insert(s, " ") for s in spaces]
        
        hint = f"{' '.join(hint)}"
        return hint

    async def get_random_word(self) -> str:
        """ Retrieve a random word from the words file"""

        with open("data/words.json", 'r') as f:
            words = json.load(f)

        return random.choice(words['words'])


    async def generate_image(self, channel_id):
        """ Given a word generate an image using DALLE from openai"""

        word = self.active_games[channel_id]
        response = openai.Image.create(prompt=random.choice(PROMPTS).format(word),n=1,size="256x256")
        image_url = response['data'][0]['url']
        res = requests.get(image_url,stream=True)

        ##NOTE: Image URLs from openai expire after 15 minutes. 
        #In order to preserve the images we
        #   save to disk and then upload to discord independently
        with open(f"image_quiz_pics/{channel_id}.png",'wb') as f:
            shutil.copyfileobj(res.raw,f)

def setup(bot):
    bot.add_cog(ImageQuizCog(bot))