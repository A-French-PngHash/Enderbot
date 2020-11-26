import utils
import random
import values
import math
import numpy
import discord
from discord.ext import commands


class TowerBossData:
    def __init__(self, floor, cnx):
        """
        Initialisation of the TowerBossData class. In the tower, the bosses and the doors have multiple positions.
        Each time the bot restart we generate new positions. This class randomly generate this positions and store them
            for each floor.

        INPUT:
            - floor : For what floor this data is
            - cnx : The connection to the database
        """

        self.floor = floor

        self.boss_pos = (random.randint(1, 8), random.randint(1, 8))
        self.up_door_pos = (random.randint(1, 8), random.randint(1, 8))
        self.down_door_pos = (random.randint(1, 8), random.randint(1, 8))
        while self.boss_pos == self.up_door_pos and self.boss_pos == self.down_door_pos:
            self.boss_pos = (random.randint(1, 8), random.randint(1, 8))
            self.up_door_pos = (random.randint(1, 8), random.randint(1, 8))
            self.down_door_pos = (random.randint(1, 8), random.randint(1, 8))
        if self.floor == 1:
            self.down_door_pos = (0, 0)
        elif self.floor == 100:
            self.up_door_pos = (0, 0)

        boss_data = values.boss_data[str(self.floor)]
        self.boss_name = boss_data["name"]
        self.boss_level = boss_data["level"]
        self.boss_hp = boss_data["hp"]
        self.boss_attack = boss_data["attack"]
        self.boss_defense = boss_data["defense"]


class Tower:
    def __init__(self, player, cnx):
        """
        Initialisation of the Tower class. The Tower is where the player can fight boss. It is composed of a 100
        different floor, each one where live a boss

        INPUT:
            - player : The player who won this tower
            - cnx : The connection to the database
        """

        self.player = player
        self.cnx = cnx
        get_data_query = f"""
            SELECT * FROM Tower
            WHERE id = {self.player.tower_id}
        """
        result = utils.execute_query(self.cnx, get_data_query)[0]
        self.id = result["id"]
        self._actual_player_floor = result["floor"]
        self._pos_x = result["pos_x"]
        self._pos_y = result["pos_y"]
        self.map = []

    @property
    def floor_data(self):
        return values.tower_data[self.actual_player_floor - 1]

    @property
    def player_pos(self):
        return self.pos_x, self.pos_y

    @property
    def pos_x(self):
        return self._pos_x

    @pos_x.setter
    def pos_x(self, value):
        query = f"""UPDATE Tower
            SET pos_x = {value};"""
        utils.execute_query(self.cnx, query)
        self._pos_x = value

    @property
    def pos_y(self):
        return self._pos_y

    @pos_y.setter
    def pos_y(self, value):
        query = f"""UPDATE Tower
        SET pos_y = {value};"""
        utils.execute_query(self.cnx, query)
        self._pos_y = value

    @property
    def actual_player_floor(self):
        return self._actual_player_floor

    @actual_player_floor.setter
    def actual_player_floor(self, value):
        query = f"""UPDATE Tower
                SET floor = {value};"""
        utils.execute_query(self.cnx, query)
        self._actual_player_floor = value

    def display_tower(self):
        """
        When the player want to fight bosses he need to see his tower. This function generates it with emojis

        OUTPUT:
             - The tower
        """
        message = f"**Floor** : {self.actual_player_floor} - {values.boss_data[str(self.actual_player_floor)]['name']}\n"
        for pos_y in range(8, 0, -1):
            self.map.append([])
            for pos_x in range(1, 9):
                pos = (pos_x, pos_y)
                emojis = values.emojis

                if self.player_pos[1] == pos[1] and self.player_pos[0] == pos[0]:
                    message += emojis["player"]
                    continue

                if self.floor_data.boss_pos == pos:
                    message += emojis["boss"]
                elif self.floor_data.up_door_pos == pos:
                    message += emojis["up_door"]
                elif self.floor_data.down_door_pos == pos:
                    message += emojis["down_door"]
                else:
                    if (pos_x + pos_y) % 2 == 1:
                        message += emojis["white_tile"]
                    else:
                        message += emojis["black_tile"]
            message += "\n"

        message += "\n\n`"
        if self.player_pos == self.floor_data.boss_pos:
            message += f"@ - You are on a boss\nBoss : {self.floor_data.boss_name}\nLevel : {self.floor_data.boss_level}\nHealth " \
                       f"points : {self.floor_data.boss_hp}\nATK : {self.floor_data.boss_attack}; DEF : {self.floor_data.boss_defense}"
        elif self.player_pos == self.floor_data.up_door_pos:
            # TODO : check if player has level
            message += "@ - ✅ You can pass !"
        elif self.player_pos == self.floor_data.down_door_pos:
            message += "@ - You are on a downstair case"
        else:
            message += "@ - You are on an empty case"
        message += f"`\n{values.emojis['energy']}You have {math.floor(self.player.energy)} energy left !"
        return message

    async def emoji_pressed(self, emoji, ctx, bot):
        """
        To move in the tower, the user press emojis. This function interpret the result of this emojis.
        """
        if self.player.energy < 1:
            return

        if emoji == "✅":
            if self.player_pos == self.floor_data.boss_pos:
                """
                FORMULES : 
                    - attaque : 
                """
                # TODO : setup the boss fight
                # This is the part that i can't do because there is a lot of formulas missing :
                #   - How many orbs do you win when you fight a boss
                #   - How is determined the number of damage you do
                #   - How do you calculate your attack points and defense points
                #   - How do you calculate your attack level ( I may actually have a solution for this : your attack_points + your defense_points passed into the normal xp formulas

                message = await ctx.send(self.attack_summary())
                await message.add_reaction("✅")
                await message.add_reaction("❌")

                def check(reaction, user):
                    return user == self.player.author and reaction.emoji in "✅❌"

                reaction, _ = await bot.wait_for("reaction_add", check=check)

                if reaction.emoji == "❌":
                    await message.edit(content="Fight canceled.")
                    return
                attack_summary = self.engage_attack()
                await ctx.send(attack_summary)


            elif self.player_pos == self.floor_data.up_door_pos:
                self.actual_player_floor += 1
            elif self.player_pos == self.floor_data.down_door_pos:
                self.actual_player_floor -= 1
            else:
                return
        elif emoji == "⬆️" and self.pos_y != 8:
            self.pos_y += 1
        elif emoji == "⬇️" and self.pos_y != 1:
            self.pos_y -= 1
        elif emoji == "➡️" and self.pos_x != 8:
            self.pos_x += 1
        elif emoji == "⬅️" and self.pos_x != 1:
            self.pos_x -= 1
        self.player.energy -= 1

    def attack_summary(self) -> str:
        """
        Before starting an attack, the player is displayed a summary which show his attack points, the boss attack etc..
        This function return this summary
        """
        boss_data = values.boss_data[str(self.actual_player_floor)]
        message = f"{self.player.author.mention} - Welcome to the guardian's lair of the stage " \
                  f"{self.actual_player_floor} : {boss_data['name']}\n"
        message += f"Your stats : HP = {round(self.player.life_points)}; " \
                   f"ATK = {round(self.player.attack)}; " \
                   f"DEF = {round(self.player.defense)}\n"
        message += f"BOSS : HP = {self.floor_data.boss_hp}; " \
                   f"ATK = {self.floor_data.boss_attack}; " \
                   f"DEF = {self.floor_data.boss_defense}\n"
        message += "Engage or retreat and may the odds be ever in your favor."
        return message

    def _get_attack_turn_message(self, turn, attacker_name, defender_name, life, total_life, damages) -> str:
        return_string = f"**TURN : {turn}** | {attacker_name} | {life}/{total_life}\n" \
                        f"{attacker_name} attacks {defender_name} who loses {damages} HPs.\n"
        return return_string

    def _calculate_fight_boss(self, floor):
        player_name = self.player.author

        turns = [""] * 4

        floor_data = values.tower_data[floor - 1]
        boss_damage_per_attack = math.floor(
            floor_data.boss_attack - self.player.defense) if self.floor_data.boss_attack > self.player.defense else 1
        if boss_damage_per_attack < 1:
            boss_damage_per_attack = 1
        player_damage_per_attack = math.floor(
            self.player.attack - floor_data.boss_defense) if self.player.attack > floor_data.boss_defense else 1
        if player_damage_per_attack < 1:
            boss_damage_per_attack = 1
        boss_life = floor_data.boss_hp
        boss_begin_life = floor_data.boss_hp
        player_life = self.player.life_points
        player_begin_life = self.player.life_points
        turn_count = 0
        while True:
            if turn_count == 0:
                turns.append(
                    self._get_attack_turn_message(turn_count, self.floor_data.boss_name, player_name, boss_life,
                                                  boss_begin_life, boss_damage_per_attack))
            turn_count += 1
            player_life -= boss_damage_per_attack
            if player_life <= 0:
                if turn_count != 0:
                    turns.append(
                        self._get_attack_turn_message(turn_count, self.floor_data.boss_name, player_name, boss_life,
                                                      boss_begin_life, boss_damage_per_attack))
                break

            turn_count += 1
            if turn_count == 1:
                turns.append(self._get_attack_turn_message(turn_count, player_name, self.floor_data.boss_name,
                                                           player_life, player_begin_life, player_damage_per_attack))
            boss_life -= player_damage_per_attack
            if boss_life <= 0:
                if turn_count != 1:
                    turns.append(
                        self._get_attack_turn_message(turn_count - 1, self.floor_data.boss_name, player_name, boss_life,
                                                      boss_begin_life, boss_damage_per_attack))
                    turns.append(
                        self._get_attack_turn_message(turn_count, player_name, self.floor_data.boss_name, player_life,
                                                      player_begin_life))
                break

        return boss_life, boss_begin_life, player_life, player_begin_life, boss_damage_per_attack, player_damage_per_attack, turn_count, turns

    def engage_attack(self) -> str:
        """
        This function is called when the player decide to attack. It perform all the necessary things to update values..

        OUTPUT:
            - str : The summary message to send to the user to inform him on what happened during the fight
        """

        boss_life, boss_begin_life, player_life, player_begin_life, boss_damage_per_attack, player_damage_per_attack, turn_count, turns = self._calculate_fight_boss(
            self.actual_player_floor)
        message = ""
        name = ""
        try:
            message = f"{self.player.author.mention}\n"
        except AttributeError:
            pass
        except Exception as error:
            raise error

        message = "\n".join(turns)
        message += "___ *** ___\n"

        if turn_count % 2 == 1:  # Player lose
            message += f"💀 {name} lost !\n{self.floor_data.boss_name} won !\n" \
                       f"You died, so you didn't get anything, also you **lost all your energy**, be more careful next" \
                       f" time, dying is not an option !"
            self.player.energy = 0
            self.player.life_points = 0
            return message

        chest_drop = ["D", "C", "B", "A", "S"]
        chest_rank = ["Common", "Unusual", "Rare", "Epic", "Legendary"]
        runes_drop = [[1, 25], [5, 50], [10, 100], [20, 200], [35, 350]]
        proba = (self.actual_player_floor % 20 * 2 + 2) / 100
        is_dropped = numpy.random.choice([True, False], p=[proba, 1 - proba])
        drop_type = self.actual_player_floor // 20 if self.actual_player_floor // 20 != 5 else 4

        message += f"**{self.floor_data.boss_name}** lost !\n👑**{name}** won !\n"
        if is_dropped:
            message += f"You just won a boss token of rank **{chest_drop[drop_type]} - {chest_rank[drop_type]}** !"
        """
        The number of runes won is determined with the distance to be able to beat the next boss times 1.5
        """
        boss_life, boss_begin_life, player_life, player_begin_life, boss_damage_per_attack, player_damage_per_attack, turn_count = self._calculate_fight_boss(
            self.actual_player_floor + 1)

        distance_new_boss = (boss_life + boss_begin_life / 2) / boss_begin_life
        if distance_new_boss < 0:
            distance_new_boss = 0
        runes_min = math.ceil(distance_new_boss * runes_drop[drop_type][0])
        runes_max = math.ceil(distance_new_boss * runes_drop[drop_type][1])
        print(runes_max)
        print(runes_min)
        return message
