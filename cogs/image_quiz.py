import disnake
import os
import requests
import openai
import shutil
import random
import json
import re
from asyncio.exceptions import TimeoutError
from disnake.ext import commands
from models.database import Database

class ImageQuizCog(commands.Cog):
    def __init__(self, bot):
        self.bot: commands.InteractionBot = bot
        self.word_api_key = os.getenv("WORDNIK_API_KEY")
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        self.db = Database()

    @commands.slash_command()
    async def imagequiz(
        self,
        ctx: disnake.ApplicationCommandInteraction) -> None:
        """
        Play a quiz where you guess the word used to generate the image
        """
        await ctx.response.defer()
        
        # Start the game
        # Listen to words entered in chat
        # If someone guesses the word award them a point
        init_game_msg = f"Starting Image Quiz!\n\nGenerating a word and an image..."
        e = disnake.Embed(description=init_game_msg)
        await ctx.send(embed=e)

        #Generate a random word 
        #r = requests.get(f"https://api.wordnik.com/v4/words.json/randomWord?hasDictionaryDef=true&includePartOfSpeech=noun&excludePartOfSpeech=adjective%2C%20verb%2C%20adverb%2C%20interjection%2C%20pronoun%2C%20preposition%2C%20abbreviation%2C%20affix%2C%20article%2C%20auxiliary-verb%2C%20conjunction%2C%20definite-article%2C%20family-name%2C%20given-name%2C%20idiom%2C%20imperative%2C%20noun-plural%2C%20noun-posessive%2C%20past-participle%2C%20phrasal-prefix%2C%20proper-noun%2C%20proper-noun-plural%2C%20proper-noun-posessive%2C%20suffix%2C%20verb-intransitive%2C%20verb-transitive&minCorpusCount=1000000&maxCorpusCount=-1&minDictionaryCount=5&maxDictionaryCount=-1&minLength=5&maxLength=-1&api_key={self.word_api_key}").json()
        #word = r.get("word").upper()


        with open("data/words.json", 'r') as f:
            words = json.load(f)

        word = random.choice(words['words'])

        print("starting image quiz with word: ", word)

        #Generate an image using openai DALLE and save it under filename ** image_quiz_<word>.png **
        response = openai.Image.create(prompt=f"A sketch of {word}",n=1,size="256x256")
        image_url = response['data'][0]['url']
        res = requests.get(image_url,stream=True)

        with open(f"temp_imagequiz.png",'wb') as f:
            shutil.copyfileobj(res.raw,f)

        #Generate hint from the word
        num_hints = 0
        hint = self.get_hint(word,num_hints)

        #Build embed with image and hint
        await ctx.edit_original_message(embed=self.get_game_embed(hint))

        def word_check(message):
            return message.channel == ctx.channel and message.content.lower() == word.lower()
        
        try:
            #Wait for a correct word or timeout and give second hint
            message: disnake.Message = await self.bot.wait_for('message', check=word_check, timeout=120)
        except TimeoutError:
            #No one guessed the word yet so give second hint
            await ctx.edit_original_message(embed=self.get_game_embed(f"**`{word}`**\nNo one guessed the word!"))
            return

        #Award whoever guessed it
        total_wins = self.db.get_image_quiz_score(message.author.id) + 1
        self.db.set_image_quiz_score(message.author.id, total_wins)
        await message.reply(f"{message.author.name} has guessed the word! It was **{word}**!\nTotal Wins: **{total_wins}**")
        
        await ctx.edit_original_message(embed=self.get_game_embed(f"**`{word}`**"))
            

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
    def get_game_embed(self, description) -> disnake.Embed:
        """ Returns an embed object with specified description """
        e = disnake.Embed(description=description)
        img = disnake.File("temp_imagequiz.png")
        e.set_image(file=img)
        return e

    def get_hint(self, word:str, amount:int)-> str:
        """ Given a word return a fancy string like ' _ e _ _ o ' for 'hello' """
        #need to preserve spaces
        spaces = [m.start() for m in re.finditer(' ',word)]

        word = word.replace(' ', '')
        hints = set()
        while len(hints) < amount:
            rnd_ltr_int = random.randint(0,len(word)-1)
            rnd_ltr = word[rnd_ltr_int]
            hints.add((rnd_ltr,rnd_ltr_int))
        
        hint = list('_'*len(word))
        for h in hints:
            hint[h[1]] = h[0]
        
        [hint.insert(s, " ") for s in spaces]
        
        hint = f"`{' '.join(hint)}`"
        return hint


def setup(bot):
    bot.add_cog(ImageQuizCog(bot))