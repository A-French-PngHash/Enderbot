import discord
import values
import utils


class Checks:
    def __init__(self, cnx):
        self.cnx = cnx

    def is_owner(self, ctx) -> bool:
        """Return if the user is the owner of the bot.

        INPUT:
            ctx : The context

        OUTPUT:
            - bool : Whether or not the user is the owner.
        """
        return ctx.author.id == values.author_id or ctx.author.id == 495656856740429824  # other test acc

    def has_account(self, user: discord.User):
        query = f"""
            SELECT * 
            FROM Player
            WHERE id = {user.id};"""
        result = utils.execute_query(self.cnx, query)
        return not (result == [])

    def create_account(self, player_id):  # Create account for the user with the corresponding id.
        print(f"creating account for player {player_id}")
        cursor = self.cnx.cursor()
        cursor.callproc("add_new_player", (player_id,))
        # Use the stored procedure named add_new_player.
        # See database construction for more information.
        cursor.close()

    def has_account_if_not_create(self, ctx):
        # Check to determine if a user has an account.
        # If not, this function will create one automatically. It always return True.
        if not self.has_account(ctx.author):
            self.create_account(ctx.author.id)
        return True
