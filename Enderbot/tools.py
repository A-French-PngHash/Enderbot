import player


class Tools:
    """Represent the tools that a player has plus their levels."""
    def __init__(self, cnx, player):
        cursor = cnx.cursor(dictionary=True)
        tools_level_querry = f"""
        SELECT * FROM Tools
        WHERE id = {player.tools_id}
        """
        cursor.execute(tools_level_querry)
        result = cursor.fetchall()[0]
        self.pickaxe = result["pickaxe_level"]
        self.sword = result["sword_level"]
        self.shield = result["shield_level"]
        self.house = result["house_level"]
        self.ring = result["ring_level"]