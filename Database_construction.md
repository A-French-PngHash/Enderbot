# Database Construction
This readme describe how the mysql database work.

# Tables
There are 3 tables :

- Player : It store data about players in general, their level, their mana. It aditionnaly store references to other tables.
- Resources : This tables store the number of resources each player have.
- Tools : This one stores all the level of the tools the user have : 
- His pickaxe
- His house
- His ring
- ...

# Player
The engine of this table is INNODB
The primary key of the table Player is the id. It is not a generated id, it is the id of the discord account which is unique.
In this table their are references to the other tables. We have a column tools_id which is asociated by a foreign key with the table Tools. We also have a column resource_id which is also asociated by a foreign key to the table Resources.
And because a drawing is better than a thousand word, here is a scheme of the table : 

| Field       | Type      | Null | Key | Default | Extra |
|-------------|-----------|------|-----|---------|-------|
| id          | bigint    | NO   | PRI | NULL    |       |
| tools_id    | mediumint | NO   | UNI | NULL    |       |
| mana        | float     | NO   |     | NULL    |       |
| xp          | int       | NO   |     | NULL    |       |
| life_points | float     | NO   |     | NULL    |       |
| resource_id | mediumint | NO   | UNI | NULL    |       |
| last_lookup | datetime  | NO   |     | NULL    |       |

# Resources
The engine of this table is INNODB
This table has again a column named "id" as primarey key. This column is generated, it increase by one each time an item is added. A foreign key is linking this id column with the resource_id column in the Player table.
This table is where all the resources are stored.
A scheme of the table : 

| Field    | Type      | Null | Key | Default | Extra          |
|----------|-----------|------|-----|---------|----------------|
| id       | mediumint | NO   | PRI | NULL    | auto_increment |
| pp       | int       | NO   |     | NULL    |                |
| am       | int       | NO   |     | NULL    |                |
| stone    | bigint    | NO   |     | NULL    |                |
| iron     | bigint    | NO   |     | NULL    |                |
| gold     | bigint    | NO   |     | NULL    |                |
| obsidian | bigint    | NO   |     | NULL    |                |
| ruby     | bigint    | NO   |     | NULL    |                |
| emerald  | bigint    | NO   |     | NULL    |                |
| sapphire | bigint    | NO   |     | NULL    |                |

# Tools
The engine of this table is INNODB.
Again, a column id auto incremented is the primary key of this table. It is linked with a foreign key to the tools_id column of the table Player.
As said earlier this table contain the levels of the tools a user has.
| Field         | Type      | Null | Key | Default | Extra          |
|---------------|-----------|------|-----|---------|----------------|
| id            | mediumint | NO   | PRI | NULL    | auto_increment |
| house_level   | tinyint   | NO   |     | NULL    |                |
| ring_level    | tinyint   | NO   |     | NULL    |                |
| sword_level   | tinyint   | NO   |     | NULL    |                |
| shield_level  | tinyint   | NO   |     | NULL    |                |
| pickaxe_level | tinyint   | NO   |     | NULL    |                |

# Stored procedures
In the database we have 1 stored procedure which is used to add a new player. It is called add_new_player and take as input the id of the player. This procedure uses transactions so there should not be any problem during the creation of a new player.
