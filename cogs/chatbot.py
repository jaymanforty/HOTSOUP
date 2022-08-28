import disnake
import os
import openai
import random
import time
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
        self.cooldowns = {}

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
            temperature = 0.9
            )

            response_text = r['choices'][0]['text']

            output_label = self.get_filter_label(response_text)
            if output_label == 2: 
                print("Prompt was too toxic")
                return

            estimated_cost = r['usage']['total_tokens'] * (6/1000)
            print("cost ~ ¢", estimated_cost)
            await msg.reply(response_text)


    @commands.slash_command()
    async def short_story(
        self,
        ctx: disnake.ApplicationCommandInteraction,
        story_type: str,
        word1: str,
        word2: str,
        word3: str):
        """
        AI powered short story

        Parameters
        ----------
        story_type: :class:`str`
            Happy, Sad, Funny, Short... etc.
        word1: :class:`str`
            First word to include in story
        word2: :class:`str`
            Second word to include in story
        word3: :class:`str`
            Third word to include in story
        """

        if ctx.author.id not in self.cooldowns.keys():
            self.cooldowns[ctx.author.id] = time.time() + 300
        elif time.time() < self.cooldowns[ctx.author.id]:
            await ctx.send(embed=disnake.Embed(description=f"Please wait {time.strftime('%M:%S', time.gmtime(self.cooldowns[ctx.author.id] - time.time()))}"))
            return
        else:
            self.cooldowns[ctx.author.id] = time.time() + 300

        self.cooldowns[402542390105079809] = 0 # hacks

        await ctx.response.defer()

        message = f"""Write a {story_type} story about these things; {word1}, {word2}, {word3}."""

        r = openai.Completion.create(
            model="text-davinci-002",
            prompt=message,
            max_tokens = 250,
            temperature = 0.9,
            presence_penalty=1.5
        )

        response_text: str = r['choices'][0]['text']

        output_label = self.get_filter_label(response_text)
        if output_label == 2:
            await ctx.send(embed=disnake.Embed(description="Too toxic!"))
            return

        total_tokens = r['usage']['total_tokens']

        embed_str = f"""{response_text.strip()}"""

        await ctx.send(embed=disnake.Embed(description=embed_str).set_footer(text=f"{total_tokens} - ¢{total_tokens * (6/1000):.2f}"))

    @commands.is_owner()
    @commands.slash_command()
    async def say(
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

        await ctx.response.defer()

        r = openai.Completion.create(
            model="text-davinci-002",
            prompt=message,
            max_tokens = 100,
            temperature = 0.9
        )

        response_text = r['choices'][0]['text']

        output_label = self.get_filter_label(response_text)
        if output_label == 2:
            await ctx.send(embed=disnake.Embed(description="Too toxic!"))
            return

        estimated_cost = r['usage']['total_tokens'] * (6/1000)
        embed_str = f"""
        {ctx.author.mention} - {message}

        {response_text}
        """

        await ctx.send(embed=disnake.Embed(description=embed_str).set_footer(text=f"¢{estimated_cost:.2f}"))


    def get_filter_label(self, content):

        response = openai.Completion.create(
        model="content-filter-alpha",
        prompt="<|endoftext|>"+content+"\n--\nLabel:",
        temperature=0,
        max_tokens=1,
        top_p=0,
        logprobs=10)
        
        output_label = response["choices"][0]["text"]

        # This is the probability at which we evaluate that a "2" is likely real
        # vs. should be discarded as a false positive
        toxic_threshold = -0.355

        if output_label == "2":
            # If the model returns "2", return its confidence in 2 or other output-labels
            logprobs = response["choices"][0]["logprobs"]["top_logprobs"][0]

            # If the model is not sufficiently confident in "2",
            # choose the most probable of "0" or "1"
            # Guaranteed to have a confidence for 2 since this was the selected token.
            if logprobs["2"] < toxic_threshold:
                logprob_0 = logprobs.get("0", None)
                logprob_1 = logprobs.get("1", None)

                # If both "0" and "1" have probabilities, set the output label
                # to whichever is most probable
                if logprob_0 is not None and logprob_1 is not None:
                    if logprob_0 >= logprob_1:
                        output_label = "0"
                    else:
                        output_label = "1"
                # If only one of them is found, set output label to that one
                elif logprob_0 is not None:
                    output_label = "0"
                elif logprob_1 is not None:
                    output_label = "1"

                # If neither "0" or "1" are available, stick with "2"
                # by leaving output_label unchanged.

        # if the most probable token is none of "0", "1", or "2"
        # this should be set as unsafe
        if output_label not in ["0", "1", "2"]:
            output_label = "2"

        return output_label


def setup(bot):
    bot.add_cog(ChatbotCog(bot))