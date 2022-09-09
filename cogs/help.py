import disnake
from disnake.ext import commands


class HelpCog(commands.Cog):
    def __init__(self, bot) -> None:
        self.bot: commands.InteractionBot = bot

    @commands.slash_command()
    async def help(
        self,
        ctx: disnake.ApplicationCommandInteraction,
        command: str = None) -> None:
        """
        Get info about commands
        """

        #If no command is supplied show user all the commands
        if not command:
            e = disnake.Embed(title="Commands")
            c_list = ''
            for c in self.bot.global_slash_commands:
                c_list += f'`/{c.name}` - {c.description}\n'
            e.description = c_list
            e.set_footer(text="For help with specific commands, run `/help <command>`")
            await ctx.send(embed=e)

        #Show command info to user
        else:
            command: commands.InvokableSlashCommand = self.bot.get_slash_command(command)

            e = disnake.Embed(title=command.name)
            e.description = command.description

            for o in command.options:
                e.add_field(name=f"*{o.name}*", value=f"*{o.description}*", inline=False)
        

            await ctx.send(embed=e)

    @help.autocomplete("command")
    async def command_autocomp(self, ctx, input):
        input=input.lower()
        return [c.name for c in self.bot.global_slash_commands if input in c.name.lower()]

def setup(bot):
    bot.add_cog(HelpCog(bot))