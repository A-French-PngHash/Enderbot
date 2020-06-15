import values
import math
import player


def format_numbers(numbers):
    """
    This function take as input a dictionary like this one : ["stone" : 1000, "Ruby" : 1000000]
    It outputs the same dictionary with the numbers as strings and with the Enderbot Number format
    where K stand for thousand, M for millions, G for billions, T for trillions, P for quadrillions
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
            if zeros[i] <= number <= zeros[i + 1]:
                number = str(round(number/(zeros[i]/100))/100) + symbol[i]
                output[key] = number
                break
    return output


def convert_resources_to_db_name(resources):
    """
    To prevent bugs and to organize things a bit more,
    in the code we only manipulate resources name as they are in the database.
    This function take as input a list of resources and return a list of resources with the appropriate names.
    """
    for (i, name) in enumerate(resources):
        if name.lower() == "perfect prism" or name.lower() == "perfect" or name.lower() == "prism":
            resources[i] = "pp"
        elif name.lower() == "anti matter" or name.lower() == "anti" or name.lower() == "matter":
            resources[i] = "am"
        else:
            resources[i] = name.lower()
    # Depending on the source of the data and because of the way the function work there may be same element two times.
    resources = list(set(resources))  # Removing duplicates

    return resources


def convert_resources_to_user_name(resources):
    """
    This will convert the list of resources taken as argument to more beautiful way of writing it.
    For example pp will become Perfect Prism and ruby will become Ruby.
    The name in the list taken as parameter must be as is it stored in the database.
    """
    for (i, name) in enumerate(resources):
        resources[i] = values.resources_name_for_user[values.resources_name_in_database.index(name)]
    return resources


def level_for(xp: int):
    """
    Take as input the number of xp the user has.
    Return the level corresponding to that number of xp.
    The formula is exponential and the max level is level 99999.
    """
    level = (1.0000001 / ((xp + 1e7 + 100) / 1e12) - 100001) * - 1
    return math.floor(level)


def get_resources_values_and_name_for(resources):
    """
    When the user input resources, for exemple in a trade, we use *arg to recolt them which mean that we need to
    transform this input into a more usable "thing" to manipulate it in the code.
    This function do this. It also convert the resources name's to db_name automatically.
    It take as argument a list of resources + their values formatted like that :
    ["stone", "65", "ruby", "9000"]
    It return a dictionary whose key are the resources name's and value the number of resources.
    """
    names = [resources[i * 2] for i in range(int(len(resources) / 2))]
    names = convert_resources_to_db_name(names)
    resources_dictionary = {}
    n = 0
    for i in range(int(len(resources) / 2)):
        resources_dictionary[names[i]] = int(resources[n + 1])
        n += 2
    return resources_dictionary


def get_trade_recap_for(resources):
    """
    When there is a trade a recap of the trade is displayed for the users.
    This functions generate a part of the recap. It takes as input a dictionary of resources formatted like this :
    ["Stone" : 65, "ruby" : 57].
    In this example it would return : "[65 <:stone:720659627934613626> Stone | 57 <:ruby:720659626260955196> Ruby]".
    If the list of resources is empty it will return "**∅ Nothing**".
    Note : If the resources name's are not formatted in a user format, it automaticaly convert them as this is suposed
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


def player_has_resources(user, resources):
    """
    Verify if a given player has the resources in his inventory.
    It take as input a player object and a dictionary.
    The dictionary "resources" is formated like that : {"stone": 65, "ruby": 57 }
    Resources name's need to be in the db format.
    """
    for (key, value) in resources.items():
        if int(user.inventory.resources[key]) < int(value):
            return False
    return True
