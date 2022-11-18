import disnake
import os
import openai
import shutil
import requests
import unicodedata
import re
from disnake.ext import commands
from models.database import Database


class ImgVoteButtons(disnake.ui.View):
        def __init__(self,image_name,image_author):
            super().__init__(timeout=None)
            self.image_name = image_name
            self.image_author = image_author
            self.db = Database()

        @disnake.ui.button(label="✔", style=disnake.enums.ButtonStyle.green)
        async def img_vote_yes_btn(self,button:disnake.ui.Button,inter:disnake.MessageInteraction):
            self.db.add_user_vote_to_image(inter.author.id,self.image_name,self.image_author,1)
            await inter.response.send_message("You voted yes",ephemeral=True)
        
        @disnake.ui.button(label="❌",style=disnake.enums.ButtonStyle.red)
        async def img_vote_no_btn(self,button:disnake.ui.Button,inter:disnake.MessageInteraction):
            self.db.add_user_vote_to_image(inter.author.id,self.image_name,self.image_author,0)
            await inter.response.send_message("You voted no",ephemeral=True)


class DalleCog(commands.Cog):
    def __init__(self,bot) -> None:
        self.bot: commands.InteractionBot = bot
        self.db = Database()
        openai.api_key = os.getenv("OPENAI_API_KEY")

    @commands.slash_command()
    async def image_hof(
        self,
        ctx: disnake.ApplicationCommandInteraction) -> None:
        """
        See top voted images generated by AI
        """
        await ctx.response.defer()

        top_5 = self.db.get_top_5_images()
        embed_lst = []
        for r in top_5:
            e = disnake.Embed(title=r[0],description=f"✅ **{r[1]}**   |   ❎ **{r[2]}**\n\nSubmitted by: <@{r[3]}>")
            e.set_image(file=disnake.File(f"dalle_pics/{r[0]}.png"))
            embed_lst.append(e)
        await ctx.send(embeds=embed_lst)

    @commands.slash_command()
    @commands.cooldown(1,120, commands.BucketType.member)
    async def create_image(
        self,
        ctx: disnake.ApplicationCommandInteraction,
        prompt: str) -> None:
        """
        AI generated image

        Parameters
        ----------
        prompt :class:`str`
            The prompt to generate an image with
        """
        await ctx.response.defer()
        response = openai.Image.create(prompt=prompt,n=1,size="1024x1024")
        image_url = response['data'][0]['url']
        res = requests.get(image_url,stream=True)

        if not os.path.exists("dalle_pics"):
            os.makedirs("dalle_pics")

        picname = self.uniquify(self.slugify(prompt))
        
        with open(f"dalle_pics/{picname}.png",'wb') as f:
            shutil.copyfileobj(res.raw,f)
        
        img = disnake.File(f"dalle_pics/{picname}.png")
        await ctx.send(file=img,view=ImgVoteButtons(picname,ctx.author.id))

    ############
    ### UTIL ###
    ############
    
    def uniquify(self, path):
        
        counter = 1
        filename = path
        
        while os.path.exists("dalle_pics/"+path+".png"):
            path = filename + " (" + str(counter) + ")"
            counter += 1

        return path

    def slugify(self, value, allow_unicode=False):
        """
        Taken from https://github.com/django/django/blob/master/django/utils/text.py
        Convert to ASCII if 'allow_unicode' is False. Convert spaces or repeated
        dashes to single dashes. Remove characters that aren't alphanumerics,
        underscores, or hyphens. Convert to lowercase. Also strip leading and
        trailing whitespace, dashes, and underscores.
        """
        value = str(value)
        if allow_unicode:
            value = unicodedata.normalize('NFKC', value)
        else:
            value = unicodedata.normalize('NFKD', value).encode('ascii', 'ignore').decode('ascii')
        value = re.sub(r'[^\w\s-]', '', value.lower())
        return re.sub(r'[-\s]+', '-', value).strip('-_')

def setup(bot):
    bot.add_cog(DalleCog(bot))