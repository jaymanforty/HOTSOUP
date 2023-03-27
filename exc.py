from disnake.ext.commands.errors import CommandError


class CustomCommandError(CommandError):
    def __init__(self, message: str = None, *args):
        self.message = message