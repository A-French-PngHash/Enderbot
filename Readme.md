# Enderbot
The rewrite in python of a multi-player RPG Discord bot with inventory, mining, crafting, boss, PVP powered by a player-driven economy & more !
# Installing
You must first install the [discord.py](https://github.com/Rapptz/discord.py) library.
You must also have installed the python [mysql connector](https://dev.mysql.com/downloads/connector/python/) as this project uses a mysql database.
You will have to build the database in order to be able to use this project. More information in the **database_construction.md** file.
You can then downoald all the file of this project, and start coding !

# Who am I and what is this about?
I'm a french student. I decided to create this project in order to up my skills in python and to learn how to use mysql.

# Specifications 
You need to store the mysql database connection information in the **config.py** file.

As the bot uses custom emojis to work you need to add all of them in a server. You then need to replace all the values in the "emojis" list in the **value.py** file by yours under this form : `<:emoji_name:emoji_id>`. You can find all the images in the Assests folder.
