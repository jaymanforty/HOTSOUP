from imp import new_module
import disnake
import os
import openai
import random
from random import randint
from disnake.ext import commands
from models.database import Database

class ChatbotCog(commands.Cog):
    def __init__(self, bot) -> None:
        self.bot: commands.InteractionBot = bot
        self.db = Database()
        openai.api_key = os.getenv("OPENAI_API_KEY")
        self.last_user_id = None
        self.allowed_channels = [798935679366594573,1007794808812740729,798935679366594574,789593992236236820]

    @commands.Cog.listener('on_message')
    async def openai_message_listener(self, msg: disnake.Message):
        
        if msg.channel.id not in self.allowed_channels: return
        if msg.author.id == self.bot.user.id: return
        if self.last_user_id == msg.author.id: return #avoids users spamming messages to get a response

        restrictions = ['https','http','<','>'] #so anything that mentions channels, has links, or has emojis wont get sent to api
        for r in restrictions: 
            if r in msg.content: return
        
        self.last_user_id = msg.author.id

        traits = ['honest','deep','humble','amusing','circumspect','restrained','selfish','apathetic','naive','Individualistic','Reliable','Felicific','Fraudulent','Frightening','Mawkish','Dry','Emotional','Busy']
        
        prompt = f"""
        The following is a conversation between two people. The other person is {','.join(random.sample(traits,k=3))}.
        {msg.author.display_name}: What do you do?
        Person#2: I reply to people.
        {msg.author.display_name}: {msg.content}
        Person#2:
        """

        if randint(1,25) == 1:
            r = openai.Completion.create(
            model="text-davinci-002",
            prompt=prompt,
            max_tokens = 50,
            temperature = 0.9)

            response_text = r['choices'][0]['text']
            estimated_cost = r['usage']['total_tokens'] * (6/1000)
            print("cost ~ ¢", estimated_cost)
            await msg.reply(response_text)

    @commands.slash_command()
    async def openai(
        self,
        ctx: disnake.ApplicationCommandInteraction,
        message: str):

        """
        AI powered response

        Parameters
        ----------
        message: :class:`str`
            The message to send to the all powerful
        """

        if len(message) > 100:
            await ctx.send(embed=disnake.Embed(description="Only a max of 100 characters in your message is allowed"), ephemeral=True)
            return 

        await ctx.response.defer()

        r = openai.Completion.create(
            model="text-davinci-002",
            prompt=message,
            max_tokens = 75,
            temperature = 0.7
        )

        response_text = r['choices'][0]['text']
        estimated_cost = r['usage']['total_tokens'] * (6/1000)
        embed_str = f"""
        {ctx.author.mention} - {message}

        {response_text}
        """

        await ctx.send(embed=disnake.Embed(description=embed_str).set_footer(text=f"¢{estimated_cost:.2f}"))





def setup(bot):
    bot.add_cog(ChatbotCog(bot))