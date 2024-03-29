import disnake
import os
import openai
import random
import time
from random import randint
from disnake.ext import commands

from constants import ALLOWED_CHANNELS


class ChatbotCog(commands.Cog):
    def __init__(self, bot) -> None:
        self.bot: commands.InteractionBot = bot
        openai.api_key = os.getenv("OPENAI_API_KEY")
        self.last_user_id = None
        self.cooldowns = {}
        self.master_convo = [{"role": "system", "content": "You have bubbly conversations with strangers on the internet."}]

    @commands.Cog.listener('on_reaction_add')
    async def cringe_react(
        self,
        reaction: disnake.Reaction,
        user: disnake.Member) -> None:
        """
        Listens for reactions that have cringe in the name to double on the cringiness
        """
        if "cringe" in reaction.emoji.name.lower():
            await reaction.message.add_reaction(reaction.emoji)
        
    @commands.Cog.listener('on_message')
    async def openai_question(
        self,
        message: disnake.Message) -> None:

        if message.author.id == self.bot.user.id: return
        if message.channel.id not in ALLOWED_CHANNELS: return
        if self.bot.user not in message.mentions: return 

        try:
            if self.cooldowns["question"] > time.time(): return
            self.cooldowns["question"] = time.time()
        except KeyError:
            self.cooldowns["question"] = time.time()

        self.master_convo.append({"role": "user", "content": f"{message.clean_content}"})

        r = openai.ChatCompletion.create(
            model="gpt-4",
            messages = self.master_convo
        )

        self.master_convo.append(r['choices'][0]['message'])
        response_text = r['choices'][0]['message']['content']

        output_label = self.get_filter_label(response_text)
        if output_label == 2: 
            print("Prompt was too toxic")
            return

        estimated_cost = (r['usage']['completion_tokens'] * (3/1000)) + (r['usage']['prompt_tokens'] * (6/1000))
        print("cost ~ ¢", estimated_cost)

        if estimated_cost >= 5: self.master_convo = [{"role": "system", "content": "You have bubbly conversations with strangers on the internet."}]

        await message.reply(f"{response_text}")
    

    @commands.Cog.listener('on_message')
    async def openai_message_listener(self, msg: disnake.Message):
        
        if msg.channel.id not in ALLOWED_CHANNELS: return
        if msg.author.id == self.bot.user.id: return
        if self.last_user_id == msg.author.id: return #avoids users spamming messages to get a response

        restrictions = ['https','http','<','>'] #so anything that mentions channels, has links, or has emojis wont get sent to api
        for r in restrictions: 
            if r in msg.content: return
        
        self.last_user_id = msg.author.id

        messages = await msg.channel.history(limit=20).flatten()
        msgs = [{"role": "system", "content": "Pretend you're in a conversation circle chiming in at the perfect moment."}]
        for m in messages:
            if not m.content: continue
            msgs.append({"role": "user", "content": f"{m.clean_content}"})

        if randint(1,25) == 1:
            r = openai.ChatCompletion.create(
            model="gpt-4",
            messages = msgs
            )

            response_text = r['choices'][0]['message']['content']

            output_label = self.get_filter_label(response_text)
            if output_label == 2: 
                print("Prompt was too toxic")
                return

            estimated_cost = (r['usage']['completion_tokens'] * (3/1000)) + (r['usage']['prompt_tokens'] * (6/1000))
            print("cost ~ ¢", estimated_cost)
            await msg.channel.send(response_text)

    # /short_story
    @commands.slash_command()
    @commands.cooldown(1,120, commands.BucketType.member)
    async def short_story(
        self,
        ctx: disnake.ApplicationCommandInteraction,
        story_type: str,
        word1: str,
        word2: str,
        word3: str,
        story_subject: str = None):
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
        story_subject: :class:`str`
            A guy falling off a ladder... etc.
        """

        await ctx.response.defer()

        message = f"""Write a {story_type} story{"" if not story_subject else f' about {story_subject}'} that contains the following subjects; {word1}, {word2}, {word3}."""

        r = openai.Completion.create(
            model="text-davinci-003",
            prompt=message,
            max_tokens = 1000,
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

        await ctx.send(embed=disnake.Embed(description=embed_str).set_footer(text=f"{total_tokens} - ¢{total_tokens * (4/1000):.2f}"))

    # /say
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
            model="text-davinci-003",
            prompt=message,
            max_tokens = 1000,
            temperature = 0.9
        )

        response_text = r['choices'][0]['text']

        output_label = self.get_filter_label(response_text)
        if output_label == 2:
            await ctx.send(embed=disnake.Embed(description="Too toxic!"))
            return

        estimated_cost = r['usage']['total_tokens'] * (4/1000)
        embed_str = f"{ctx.author.mention} - {message}"
        embed_str += f"{response_text}"

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