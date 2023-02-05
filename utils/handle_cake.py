import json


class CakeHandler:
    def __init__(self, filename: str):
        """This function initializes the Cake Handler.
        It loads a cake from a json and fills the attributes with the loaded cake

        Arguments:
            filename -- cake filename
        """
        try:
            with open(filename, "r") as file:
                cake: dict = json.load(file)
        except Exception as E:
            raise (E)

        self.characters = cake["characters"]

        self.account = cake["account"]

        self.char_name_map = {
            i: cake_char["name"] for i, cake_char in enumerate(self.characters)
        }

    def __len__(
        self,
    ):
        """This function runs when the len operation is called. Returns the len of characters

        Returns:
            Number of characters
        """
        return len(self.characters)

    def get_character_name(self, id: int):
        """Get Character name from Character id

        Arguments:
            id -- Character id

        Returns:
            Character name
        """
        return self.char_name_map.get(id, "Invalid character Id")

    def get_char_inventory(self, char_id):
        """Get Char inventory by Character id

        Arguments:
            char_id -- Character Id

        Returns:
            Character Inventory bag items
        """
        inventory = self.characters[char_id]["inventory"]

        used_inventory = {}
        for item_dict in inventory:
            item_name: str = list(item_dict)[0]
            if item_name not in ["None", "LockedInvSpace"]:
                item_qty = item_dict[item_name]
                if used_inventory.get(item_name):
                    used_inventory[item_name] += item_qty
                else:
                    used_inventory[item_name] = item_qty
        return used_inventory

    def get_chest_inventory(self) -> dict:
        """Get account chest inventory

        Returns:
            Account chest items
        """
        inventory = self.account["chest"]

        used_inventory = {}
        for item_dict in inventory:
            item_name: str = list(item_dict)[0]
            if item_name not in ["None", "LockedInvSpace"]:
                item_qty = item_dict[item_name]
                if used_inventory.get(item_name):
                    used_inventory[item_name] += item_qty
                else:
                    used_inventory[item_name] = item_qty
        return used_inventory
