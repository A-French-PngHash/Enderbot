import discord
import player
import values
import utils

class Drop:
    def __init__(self, player, resources, channel_id, cnx):
        """
        Initialisation of the Drop class. This class represent some resources dropped by a player in a channel.
        """
        self.player = player
        self.cnx = cnx
        self.resources = resources
        self.channel_id = channel_id

    def get_drop_confirmation_message(self) -> str:
        """
        Before a drop the bot ask the confirmation. This function return the message who need to be sent to the user

        OUTPUT:
            - str : The message to sedn to the user
        """
        message = f"{self.player.author.mention} - Please confirm that you want to drop the following resources : "
        for (key, value) in self.resources.items():

            name_user_format = utils.convert_resources_to_user_name([key])[0]
            message += str(value) + " " + values.emojis[name_user_format] + " " + name_user_format
        message += "Stone Anyone will be able to get it in this channel with the command >pickup"
        return message
        # TODO : finish drop

    def do_drop(self):
        query = f"""
        START TRANSACTION;
        INSERT INTO Resources
        SET 
        """
        for (key, value) in self.resources.items():
            query += f"{key}={value},"
        query = query[-1:]
        query += "SELECT LAST_INSERT_ID() INTO @resourceid;"
        query += f"""
        INSERT INTO ResourcesDropped
        VALUES({self.channel_id}, {self.player.id}, @resourceid);
        COMMIT;
        """
