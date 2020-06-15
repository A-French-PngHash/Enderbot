import discord


class DefaultError(Exception):
    """
    All the error that we create inherit from this class.
    They all need to have at least a method str and a method get_message.
    """
    def __str__(self):
        return "Unknown error"

    def get_message(self):
        """Return a custom message that need to be printed in order to give the user informations about what
        happened.
        We can't use the __str__ method to show the message because if we do it also show the name of the class
        which is something the user don't want."""
        return "Unknown error"


class NotEnoughResourcesError(DefaultError):
    def __init__(self, author: discord.Member):
        self.author = author

    def __str__(self):
        return f"Player {self.author.mention} don't have enough resources..."

    def get_message(self):
        return f"Player {self.author.mention} don't have enough resources..."