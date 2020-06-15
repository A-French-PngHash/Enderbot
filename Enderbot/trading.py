import player
import utils
from errors import *


class Trade:
    """
    This class represent a trade between two players.
    """
    def __init__(self, trading_player: player.Player, mentioned_player: player.Player, given_resources,
                 received_resources):
        """
        This init take as input two player object. The one that started the trade and the one that is mentioned in.
        It also take two dictionaries. The resource given by the trading_player and the resource given by the
        mentioned_player.
        This two dictionaries are formated like that : {"stone": 65, "ruby": 57 }
        Resources name's need to be in the db format.
        """
        self.trading_player = trading_player
        self.mentioned_player = mentioned_player
        self.given_resources = given_resources
        self.received_resources = received_resources
        if not utils.player_has_resources(trading_player, given_resources):
            raise NotEnoughResourcesError(trading_player.author)
        self.trading_player_validation = len(given_resources) == 0
        self.mentioned_player_validation = len(received_resources) == 0
        # If no resource is given/received then the player that don't send resources don't need to accept.

    def get_trade_recap(self, status) -> str:
        """
        This function return a message that can be send in discord to inform the users of the trade going on.
        It takes as input the status of the trade. Whether it's completed or not.
        """
        message_body = f"**Transaction order**\nPlayer {self.trading_player.author.mention} **proposes to give** {utils.get_trade_recap_for(self.given_resources)}\nPlayer {self.mentioned_player.author.mention} **is asked to give** {utils.get_trade_recap_for(self.received_resources)}\n"
        message_status = f"Status : **Pending...** :interrobang:\n"
        message_end = "*If both players agree about this trade, please add both :white_check_mark: as reaction on this message, once done, transaction will be confirmed.* "
        if status == "waiting" and len(self.received_resources) == 0:
            message_end = "*Since it is a direct donation, only your confirmation is necessary to finalize the transaction, just add :white_check_mark: as reaction on this message, once done, transaction will be confirmed.*"
        elif status == "canceled":  # TODO : Add canceled message.
            message_status = f"Status : **Canceled** :x: (Reason: Cancel asked by one of the players\n"
            message_end = ""
        elif status == "succeeded":
            message_status = "Status : Confirmed :white_check_mark:"
            message_end = ""
        return message_body+message_status+message_end

    def is_possible(self) -> bool:
        # Return if the trade is possible or not
        return self.trading_player_validation and self.mentioned_player_validation

    async def do_trade(self, message):
        """
        This function execute the trade. It performs all necessary request to update the database.
        It take as input a discord.Message object in order to be able to edit it.
        """
        if len(self.received_resources) > 0:
            self.trading_player.receive_resource_from(self.received_resources, self.mentioned_player)
        if len(self.given_resources) > 0:
            self.mentioned_player.receive_resource_from(self.given_resources, self.trading_player)
        await message.edit(content=self.get_trade_recap("succeeded"))
