import disnake
import os
import datetime
import requests 

from disnake.ext import commands
from models.database import Database

class WOTDCog(commands.Cog):
    def __init__(self, bot) -> None:
        self.bot: commands.InteractionBot = bot
        self.api_key = os.getenv("WORDNIK_API_KEY")
        self.mw_api_key = os.getenv("MW_DICT_API_KEY")
        self.db = Database()

    #TODO
    @commands.slash_command()
    async def bind_wotd(
        self,
        ctx: disnake.ApplicationCommandInteraction,
        channel: disnake.TextChannel = None) -> None:
        """
        Bind a text channel to display a word of the day that auto updates

        Parameters
        ----------
        channel: :class:`disnake.TextChannel`
            The channel to bind to. Default is current channel.
        """
        await ctx.send("Check back later", ephemeral=True)

    
    @commands.slash_command()
    async def randomword(
        self,
        ctx: disnake.ApplicationCommandInteraction) -> None:
        """
        Generate a random word
        """
        await ctx.response.defer()
        r = requests.get(f"https://api.wordnik.com/v4/words.json/randomWord?hasDictionaryDef=true&includePartOfSpeech=noun%2C%20adjective%2C%20verb%2C%20adverb&minCorpusCount=50&maxCorpusCount=-1&minDictionaryCount=1&maxDictionaryCount=-1&minLength=5&maxLength=-1&api_key={self.api_key}").json()
        word = r.get("word")
        definitions = await self.get_defintions(word)
        #pronounce = await self.get_pronounciation(word)

        e = disnake.Embed(title=word)
        for meta in definitions:
            def_str = f""
            for d in definitions[meta]['definitions']:
                def_str += f"- {d}\n"

            e.add_field(meta.split(":")[0] + f" ({definitions[meta]['label']})", def_str, inline=False)
        
        await ctx.send(embed=e)

    @commands.slash_command()
    async def wotd(
        self,
        ctx: disnake.ApplicationCommandInteraction,
        date: str = None) -> None:
        """
        Query the word of the day

        Parameters
        ----------
        date: :class:`str`
            YYYY-MM-DD date format
        """
        if date != None:
            try:
                datetime.datetime.strptime(date, '%Y-%m-%d').date()
            except ValueError:
                await ctx.send(embed=disnake.Embed(description="Invalid date! YYYY-MM-DD"), ephemeral=True)
                return
        else:
            date = str(datetime.date.today())

        await ctx.response.defer()
        try:
            r = requests.get(f"https://api.wordnik.com/v4/words.json/wordOfTheDay?date={date}&api_key={self.api_key}").json()
        except Exception as e:
            print(e)
            await ctx.send("There was an error :(", ephemeral=True)
            return

        word = r.get("word")
        definitions = await self.get_defintions(word)

        e = disnake.Embed(title=word)
        for meta in definitions:
            def_str = f""
            for d in definitions[meta]['definitions']:
                def_str += f"- {d}\n"

            e.add_field(meta.split(":")[0] + f" ({definitions[meta]['label']})", def_str, inline=False)
        
        await ctx.send(embed=e)

    async def get_pronounciation(self, word: str) -> str:
        try:
            url = f"https://api.wordnik.com/v4/word.json/{word}/pronunciations?useCanonical=false&limit=1&api_key={self.api_key}"
            r = requests.get(url).json()[0]
            return r.get("raw")
        except: KeyError

    async def get_defintions(self, word: str) -> dict:
        """ Returns info about a word using api calls """
        url = f"https://www.dictionaryapi.com/api/v3/references/collegiate/json/{word}?key={self.mw_api_key}"
        r = requests.get(url).json()
        d_dict = {}
        for k in r:
            try:
                k.get("meta").get("id")
                #if k.get("meta").get("id").split(":")[0] != word: continue
            except AttributeError:
                d_dict["No Definitions found.. Maybe you meant..."] = {"label": "", "definitions":r}
                return d_dict

            d_dict[k.get("meta").get("id")] = {"label": k.get("fl"), "definitions": k.get('shortdef')}

        return d_dict

def setup(bot):
    bot.add_cog(WOTDCog(bot))