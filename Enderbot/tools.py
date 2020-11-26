import player
import utils


class Tools:
    """Represent the tools that a player has plus their levels."""
    def __init__(self, cnx, player):
        tools_level_querry = f"""
        SELECT * FROM Tools
        WHERE id = {player.tools_id}
        """
        result = utils.execute_query(cnx, tools_level_querry)[0]
        self.pickaxe = result["pickaxe_level"]
        self.sword = result["sword_level"]
        self.shield = result["shield_level"]
        self.house = result["house_level"]
        self.ring = result["ring_level"]