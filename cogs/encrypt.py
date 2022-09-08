import disnake
import os
from cryptography.fernet import Fernet
from disnake.ext import commands

class EncryptCog(commands.Cog):
    def __init__(self, bot) -> None:
        self.bot:commands.InteractionBot = bot
        self.create_key()

    def create_key(self):
        if os.path.exists("secret.key"): 
            self.key = Fernet(open("secret.key","rb").read())
        else:
            key = Fernet.generate_key()
            with open("secret.key", "wb") as f:
                f.write(key)


    @commands.slash_command()
    async def encrypt(
        self,
        ctx: disnake.ApplicationCommandInteraction,
        msg: str) -> None:
        """
        Encrypt some data... Commands aren't encrypted tho so discord still sees 0-0

        Parameters
        ----------
        msg: :class:`str`
            The data to encrypt
        """
        encrypted_message = self.key.encrypt(msg.encode())
        await ctx.send(embed=disnake.Embed(description=encrypted_message.decode()), ephemeral=True)

    @commands.slash_command()
    async def decrypt(
        self,
        ctx: disnake.ApplicationCommandInteraction,
        msg: str) -> None:
        """
        Decrypt some data

        Parameters
        ----------
        msg: :class:`str`
            The data to decrypt
        """
        d_msg = self.key.decrypt(msg.encode())
        await ctx.send(embed=disnake.Embed(description=d_msg.decode()), ephemeral=True)



def setup(bot):
    bot.add_cog(EncryptCog(bot))