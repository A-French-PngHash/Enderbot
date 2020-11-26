import sys
import subprocess
import platform
import json
import os





def get_data():
    dir_path = os.path.dirname(os.path.realpath(__file__))
    with open(f"{dir_path}/data/project_data.json") as json_file:
        data = json.load(json_file)
        return data


def write_to_json(data):
    dir_path = os.path.dirname(os.path.realpath(__file__))
    with open(f"{dir_path}/data/project_data.json", 'w') as outfile:
        json.dump(data, outfile)

def clear_console():
    command = "cls" if platform.system().lower()=="windows" else "clear"
    return subprocess.call(command) == 0


def install_packages():
    clear_console()
    print("Installing requirements...")
    packages = ["discord.py", "mysql-connector-python"]
    for package in packages:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])

    clear_console()
    print("Pip requirements installed !")
    print("You need to install mysql to your machine because this bot uses a mysql database as storage. If you don't "
          "already installed it, install it here : https://dev.mysql.com/downloads/mysql/#downloads")
    input("Press enter to continue")
    clear_console()


def enter_data():
    clear_console()
    print("Now I will need to collect some data in order to setup the bot.")
    print("The data is stored in data/project_data.json and nothing is sent over the internet")
    owner_id = input("Enter the id of your main account (used to allow only you to do admin commands) : ")
    bot_id = input("Enter the id of your bot : ")
    bot_token = input("Enter the token of your bot : ")
    data = get_data()
    data["author_id"] = owner_id
    data["bot_id"] = bot_id
    data["bot_token"] = bot_token
    write_to_json(data)
    clear_console()


def enter_mysql_data():
    clear_console()
    print(
        "By default your ip to connect to mysql database is localhost because this installation assistant will "
        "install the database locally.")
    change_ip_choice = input("Press Y if you wish to change it. Else press enter").lower()
    mysql_ip = "localhost"
    if change_ip_choice == "y":
        mysql_ip = input("Please enter the ip used to connect to the database")
    mysql_user = input(
        "Please enter the user you want to connect to the database with (make sure it has the create database "
        "permissions) : ")
    mysql_password = input("Enter the password used to connect with this user : ")

    data = get_data()
    data["mysql_db_ip"] = mysql_ip
    data["mysql_db_user"] = mysql_user
    data["mysql_db_password"] = mysql_password
    write_to_json(data)
    clear_console()


def setup_database(complete_installation):
    import mysql.connector
    clear_console()
    print("Note that you need to have mysql connector installed and mysql installed on your device.")
    database_name = input("I am now going to setup the database, how do you wish to call it : ")
    data = get_data()
    data["mysql_db_name"] = database_name

    cnx = mysql.connector.connect(
        user=data["mysql_db_user"],
        password=data["mysql_db_password"],
        host=data["mysql_db_ip"],
        use_pure=True)
    cursor = cnx.cursor()
    cursor.execute(f"DROP DATABASE IF EXISTS {database_name}")
    cursor.execute(f"CREATE DATABASE {database_name}")
    cursor.close()

    source_file = f"{os.getcwd()}/Database.sql"
    command = """mysql -u %s -p"%s" --host %s --port %s %s < %s""" % (data["mysql_db_user"], data["mysql_db_password"], data["mysql_db_ip"], 3306, database_name, source_file)
    os.system(command)

    write_to_json(data)
    #clear_console()
    print("Database was succesfully created.")
    if complete_installation:
        print("The installation is now complete. You can now start the bot by starting the main.py file. You have "
              "access with your main account to administrations commands.")
        print("All the data you just entered is stored in the Enderbot/project_data.json file")



while True:
    print("Welcome to the installer assistant. You can choose one of the options or just do everything for a clean and "
      "normal installation")
    print("------------------------------")
    print("0 : Do the normal install which will go through all the steps bellow")
    print("1 : Verify and install requirements")
    print("2 : Enter bot and owner data")
    print("3 : Enter mysql connection identifier")
    print("4 : Setup database")

    try:
        choice = int(input("Choose your option : "))
    except:
        choice = -1
        clear_console()
    do_all = choice == 0

    if choice == 1 or do_all:
        install_packages()
    if choice == 2 or do_all:
        enter_data()
    if choice == 3 or do_all:
        enter_mysql_data()
    if choice == 4 or do_all:
        setup_database(do_all)
