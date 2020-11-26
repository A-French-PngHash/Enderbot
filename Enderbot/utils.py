import values
import math
import player
import discord
import datetime
import mysql.connector


def format_numbers(numbers):
    """

    INPUT:
        - A dictionary formatted this one : {"stone" : 1000, "Ruby" : 1000000}

    OUTPUT:
        - dictionary : It outputs the same dictionary with the numbers as strings and with the Enderbot Number format
            where K stand for thousand, M for millions, G for billions, T for trillions, P for quadrillions.
    """
    output = {}
    for (key, element) in numbers.items():
        zeros = [1000, 1000000, 1000000000, 1000000000000, 1000000000000000, 1000000000000000000]
        # Impossible to go higher than the last one, it is the limit.
        symbol = ["K", "M", "G", "T", "P"]
        number = element
        if element < 1000:
            output[key] = str(element)
            continue
        for i in range(len(zeros) - 1):
            if zeros[i] <= number < zeros[i + 1]:
                number = str(round(number/(zeros[i]/100))/100) + symbol[i]
                output[key] = number
                break
    return output


def convert_resources_to_db_name(resources):
    """
    To prevent bugs and to organize things a bit more,
        in the code we only manipulate resources name as they are in the database.

    INPUT:
        - resources : A list of resources

    OUTPUT:
         - list : The list of resources with the appropriate names.
    """
    for (i, name) in enumerate(resources):
        if name.lower() == "perfect prism" or name.lower() == "perfect" or name.lower() == "prism":
            resources[i] = "pp"
        elif name.lower() == "anti matter" or name.lower() == "anti" or name.lower() == "matter" or name.lower() == "antimatter":
            resources[i] = "am"
        else:
            resources[i] = name.lower()
    # Depending on the source of the data and because of the way the function work there may be same element two times.
    resources = list(set(resources))  # Removing duplicates

    return resources


def convert_resources_to_user_name(resources):
    """
    This function will convert the list of resources taken as argument to more beautiful way of writing it.
    For example "pp" will become "Perfect Prism" and "ruby" will become "Ruby".
    The name in the list taken as parameter must be as is it stored in the database.

    INPUT:
        - Resources : A list of resources

    OUTPUT:
        - list : The resources but writen better

    """
    for (i, name) in enumerate(resources):
        resources[i] = values.resources_name_for_user[values.resources_name_in_database.index(name)]
    return resources


def level_for(xp: int):
    """
    Calculate the level depending of the xp. The formula is exponential and the max level is level 99999.

    INPUT:
        - xp:int : The number of xp the user has.

    OUTPUT:
        - int : The level corresponding to that number of xp
    """

    # level = (1.0000001 / ((xp + 1e7 + 100) / 1e12) - 100001) * - 1 <-- This formula work too. It seems not to be the official
    level = 1+xp/(100+(1+xp/100)/1000)
    return math.floor(level)


def get_resources_values_and_name_for(resources):
    """
    When the user input resources, for example in a trade, we use *arg to collect them which mean that we need to
    transform this input into a more usable "thing" to manipulate it in the code.
    This function do this. It also convert the resources name's to db_name automatically.

    INPUT :
        - resources : a list of resources + their values formatted like that : ["stone", "65", "ruby", "9000"]

    OUPUT :
        - dictionary : A dictionary whose key are the resources name's and value the number of resources.
    """
    resources_dict = {resources[i]:int(resources[i+1]) for i in range(0, len(resources), 2)}
    return resources_dict


def get_trade_recap_for(resources):
    """
    When there is a trade, a recap of the trade is displayed for the users.
    This functions generate a part of this recap.

    INPUT:
        - resources : A dictionary of resources formatted like this : ["Stone" : 65, "ruby" : 57].

    OUTPUT :
        - str : The part of the recap.
            In this example it would return : "[65 <:stone:720659627934613626> Stone | 57 <:ruby:720659626260955196> Ruby]".
            If the list of resources is empty it will return "**∅ Nothing**".

    Note : If the resources name's are not formatted in a user format, it automatically convert them as this is supposed
    to appear on the recap message.
    """

    if len(resources) == 0:
        return "**∅ Nothing**"
    return_string = "["
    for (name, value) in resources.items():
        if len(return_string) > 1:
            return_string += " | "
        name_user_format = convert_resources_to_user_name([name])[0]
        return_string += str(value) + " " + values.emojis[name_user_format] + " " + name_user_format
    return_string += "]"
    return return_string


def get_mine_embed(resources_dropped, user, mana_used, xp_dropped):
    """
    After doing a mine, the user get an embed which said how many resources he won etc...
    This function return this embed.

    INPUT:
        - resources_dropped : The list of the resources dropped
        - user : The player object in order to display additional data
        - mana_used : The number of mana_used in this mine
        - xp_dropped : The number of xp dropped

    OUTPUT:
        - The embed generated
    """
    embed = discord.Embed(color=0xff9200)
    embed.set_author(name=user.author.name, icon_url=user.author.avatar_url)
    resources_gained = ""
    for i in values.resources_name_in_database:
        name_as_user = convert_resources_to_user_name([i])[0]
        if resources_dropped[i] != 0:
            resources_gained += values.emojis[name_as_user] + " " + name_as_user + ": " + add_space_number(resources_dropped[i]) + "\n"
    embed.add_field(name = "Resources mined", value=resources_gained, inline=True)
    embed.add_field(name = "Information", value=f"{values.emojis['mana']} Mana used: {add_space_number(mana_used)}\n"
                                                f"{values.emojis['mana']} Mana remaining: {add_space_number(math.floor(user.mana))}\n"
                                                f"{values.emojis['xp']} Exp Gained: {add_space_number(xp_dropped)}\n"
                                                f"{values.emojis['pickaxe']} Maximum theoretical critical: {add_space_number(user.critical)}", inline=True)
    return embed


def add_space_number(number):
    """A simple function to add a space every three 0 for exemple :
    '14376' -> '14 376'

    INPUT:
        - number : The string or int to convert.

    OUPUTS:
        - The result of the query"""

    def split(string):
        while string:
            yield string[:3]
            string = string[3:]

    return " ".join(list(split(str(number)[::-1])))[::-1]


def set_value_for(player, new_value, name, cnx):
    """This basic function can execute simple queries onto players objects in the database.

    INPUTS :
        - player : A player object used to add a WHERE clause in the query
        - new_value : The new value to set the column to
        - name : The name of the column.
        - cnx : The connection to the database.
    """

    query = f"""
    UPDATE Player
    SET {name} = {new_value}
    WHERE id = {player.id};"""
    execute_query(cnx, query)


def execute_query(cnx, query):
    """Use to execute queries to the database.

    INPUT :
        - cnx : A connection to the mysql database to execute queries
        - query : The query itself."""
    cursor = cnx.cursor(dictionary=True)
    print(query)
    cursor.execute(query)
    results = None
    try:
        results = cursor.fetchall()
    except mysql.connector.Error as err:
        pass
    cursor.close()
    return results


async def add_validation_emojis_to_message(message : discord.Message):
    """This function add the ✅ and ❌ reactions to the message.
    INPUT:
        - message : The message on which the program has to add the reactions.
    """

    await message.add_reaction("✅")
    await message.add_reaction("❌")


def get_remaining_time(end_date) -> (int, int):
    """
    This function return the minutes and the second that are left until the end_date.

    INPUT:
        - end_date : The end time

    OUTPUT:
        - int : The minutes remaining
        - int : The seconds remaining
    """
    interval_between_release = end_date - datetime.datetime.today()
    if interval_between_release.total_seconds() < 0:
        return (0, 0)
    minutes = interval_between_release.seconds // 60
    seconds = interval_between_release.seconds % 60
    return minutes, seconds

def reset_account(cnx, id):
    """
    Called when needing to reset the account

    INPUT :
        - id : The id of the account to reset
    """
    cursor = cnx.cursor()
    cursor.callproc("drop_player", (id,))
    cursor.callproc("add_new_player", (id,))
    cursor.close()