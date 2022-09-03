from colorsys import hls_to_rgb, rgb_to_hls
import disnake
import qrcode
import random as rnd
from disnake.ext import commands

class QRCog(commands.Cog):
    def __init__(self, bot) -> None:
        self.bot: commands.InteractionBot = bot


    @commands.slash_command()
    async def qrcode(
        self,
        ctx: disnake.ApplicationCommandInteraction,
        data: str) -> None:
        """
        Generate a QR Code with whatever data you want

        Parameters
        ----------
        data: :class:`str`
            The data to put into the QR code
        """
        qr = qrcode.QRCode(version=1,
                            box_size=10,
                            border = 5)

        qr.add_data(data)
        qr.make(fit=True)
        
        rgb = self.random_rgb()
        rgb2 = self.get_complimentary_rgb(rgb[0],rgb[1],rgb[2])
        img = qr.make_image(fill_color=int(self.rgb_to_hex(rgb),16),
                            back_color=int(self.rgb_to_hex(rgb2),16))
        img.save("temp_qrcode.png")
        img = disnake.File('temp_qrcode.png')
        await ctx.send(file=img)
    
    def get_complimentary_rgb(self, r,g,b):
        h,l,s = rgb_to_hls(r/255,g/255,b/255)
        h = h+0.5 if h+0.5 < 1.0 else 1-(h+0.5)
        r,g,b = hls_to_rgb(h,l,s)
        return (round(r*255),round(g*255),round(b*255))

    def random_rgb(self):
        rgb = [rnd.randint(0,255),rnd.randint(0,255),rnd.randint(0,255)]
        rnd.shuffle(rgb)
        return tuple(rgb)

    def rgb_to_hex(self, rgb):
        return '%02x%02x%02x' % rgb

def setup(bot):
    bot.add_cog(QRCog(bot))