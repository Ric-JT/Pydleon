import json
from typing import List, Dict, Union

from resources.template_data import stone_upgrade_template
from maps.itemMap import item_map
from maps.cardEquipMap import card_equip_map
from maps.talentMap import talent_map
from maps.classTalentMap import (
    class_index_map,
    class_talent_map,
    class_talent_page_map,
)
from maps.maps import (
    obol_name_map,
    card_set_map,
    skill_index_map,
    star_sign_map,
    fishing_bait_map,
    fishing_line_map,
    large_bubble_map,
)

UNKNOWN = "UNKNOWN"


class RawFieldParser:
    def __init__(self, fields: dict) -> None:
        self.fields: dict = fields

    def _get_straight_field_data(
        self, src_field_name: str, default_type: str = None
    ) -> object:
        if default_type is None:
            default_type: str = src_field_name.replace("_", "").upper()
        default_value: str = f"{UNKNOWN}-{default_type}"

        return self.fields.get(src_field_name, default_value)

    def _apply_map(
        self,
        array: Union[list, dict],
        map: dict,
        element_prefix: str = "",
        field_unknown: str = "",
    ) -> list:
        output_list = []
        for el in array:
            if el != "length":

                if type(array) == list:
                    if type(el) == str:
                        key = element_prefix + el  # .upper()

                    else:
                        key = el
                elif type(array) == dict:
                    key = array[el]

                elif type(array) == int:
                    key = f"{el}"
                else:
                    print(f"Type of array: {type(array)}", array)
                message_parts = [UNKNOWN, f"{key}"]
                if len(field_unknown):
                    message_parts += [field_unknown.upper()]
                message = "-".join(message_parts)
                value = map.get(key, message)
                if UNKNOWN in value:
                    print("Unknown:", value)

                output_list += [value]
        return output_list

    def _get_stone_upgrades(self, plain_data: List[Dict[str, int]], char_i: int):
        StoneData = json.loads(self.fields[f"EMm0_{char_i}"])
        # add blank data to everything in the list first
        for j in range(len(plain_data)):
            plain_data[j]["stoneData"] = stone_upgrade_template

        # go through stone data and add any that need to be added
        keys = StoneData.keys()
        for key in keys:
            # (hacky fix) some weapon power is stored as "Weapon_Power" instead of "Power"
            # if that happens, just add "Power" with the same value
            if "Weapon_Power" in StoneData[key].keys():
                StoneData[key]["Power"] = StoneData[key]["Weapon_Power"]

            plain_data[int(key)]["stoneData"] = StoneData[key]
        return plain_data

    def _get_armor(
        self,
        equipable_names: List[Dict[str, str]],
        equipable_counts: List[Dict[str, int]],
        char_i: int,
    ) -> List[Dict[str, object]]:

        raw_equipment_names = self._apply_map(
            equipable_names[0], item_map, field_unknown="armor"
        )
        raw_equipment_counts = [
            equipable_counts[0][equip_name]
            for equip_name in equipable_counts[0]
            if equip_name != "length"
        ]

        plain_equipment_data = [
            {equip_name: count}
            for equip_name, count in zip(raw_equipment_names, raw_equipment_counts)
        ]

        plain_equipment_data = self._get_stone_upgrades(plain_equipment_data, char_i)
        return plain_equipment_data

    def _get_tools(
        self,
        equipable_names: List[Dict[str, str]],
        equipable_counts: List[Dict[str, int]],
        char_i: int,
    ):
        raw_tool_names = self._apply_map(
            equipable_names[1], item_map, field_unknown="tool"
        )
        raw_tool_counts = [
            equipable_counts[1][tool_name]
            for tool_name in equipable_counts[1]
            if tool_name != "length"
        ]

        plain_tool_data = [
            {tool_name: count}
            for tool_name, count in zip(raw_tool_names, raw_tool_counts)
        ]

        plain_tool_data = self._get_stone_upgrades(plain_tool_data, char_i)
        return plain_tool_data

    def _get_foods(
        self,
        equipable_names: List[Dict[str, str]],
        equipable_counts: List[Dict[str, int]],
        char_i: int,
    ):
        raw_food_names = self._apply_map(
            equipable_names[2], item_map, field_unknown="food"
        )
        raw_food_counts = [
            equipable_counts[2][food_name]
            for food_name in equipable_counts[2]
            if food_name != "length"
        ]

        plain_food_data = [
            {food_name: count}
            for food_name, count in zip(raw_food_names, raw_food_counts)
        ]

        return plain_food_data

    def get_char_class(self, char_i: int) -> str:
        default_type: str = "CHARCLASS"
        src_field_name: str = f"CharacterClass_{char_i}"
        raw_data = self._get_straight_field_data(src_field_name, default_type)
        return self._apply_map([raw_data], class_index_map, field_unknown="charclass")[
            0
        ]

    def get_char_money(self, char_i: int) -> float:
        default_type: str = "MONEY"
        src_field_name: str = f"Money_{char_i}"
        return self._get_straight_field_data(src_field_name, default_type=default_type)

    def get_char_AFKtarget(self, char_i: int) -> str:
        default_type: str = "AFKTARGET"
        src_field_name: str = f"AFKtarget_{char_i}"

        afk_target: str = self._get_straight_field_data(
            src_field_name, default_type=default_type
        )
        return afk_target.capitalize()

    def get_char_currentMap(self, char_i: int) -> int:
        default_type: str = "CURRENTMAP"
        src_field_name: str = f"CurrentMap_{char_i}"
        return self._get_straight_field_data(src_field_name, default_type=default_type)

    def get_char_npcDialog(self, char_i: int) -> Dict[str, int]:
        default_type: str = "NPCDIALOG"
        src_field_name: str = f"NPCdialogue_{char_i}"

        json_str: str = self._get_straight_field_data(
            src_field_name, default_type=default_type
        )
        dialogs_completed: Dict[str, int] = json.loads(json_str)
        return dialogs_completed

    def get_char_AFKtime(self, char_i: int) -> float:
        default_type: str = "TIMEAWAY"
        src_field_name: str = f"PTimeAway_{char_i}"

        AFKtime: float = self._get_straight_field_data(
            src_field_name, default_type=default_type
        )
        return AFKtime

    def get_char_instaRevives(self, char_i: int) -> int:
        default_type: str = "INSTAREVIVES"
        src_field_name: str = f"PVInstaRevives_{char_i}"
        return self._get_straight_field_data(src_field_name, default_type=default_type)

    def get_char_gender(self, char_i: int) -> str:
        default_type: str = "GENDER"
        src_field_name: str = f"PVGender_{char_i}"
        gender_int: int = self._get_straight_field_data(
            src_field_name, default_type=default_type
        )

        gender: str = "Pees standing up" if gender_int == 0 else "Pees seating down"
        return gender

    def get_char_minigames(self, char_i: int) -> int:
        default_type: str = "MINIGAMEPLAYS"
        src_field_name: str = f"PVMinigamePlays_{char_i}"
        return self._get_straight_field_data(src_field_name, default_type=default_type)

    def get_char_statlist(self, char_i: int) -> Dict[str, int]:
        default_type: str = "STATLIST"
        src_field_name: str = f"PVStatList_{char_i}"
        columns: List[str] = ["strength", "agility", "wisdom", "luck", "level"]
        statlist: List[int] = self._get_straight_field_data(
            src_field_name, default_type=default_type
        )

        stat_dict: Dict[str, int] = {}
        for stat_name, stat_value in zip(columns, statlist):
            stat_dict[stat_name]: int = stat_value

        return stat_dict

    def get_char_POBoxUpgrades(self, char_i: int) -> List[int]:
        default_type: str = "POBOXUPGRADES"
        src_field_name: str = f"POu_{char_i}"
        return json.loads(
            self._get_straight_field_data(src_field_name, default_type=default_type)
        )

    def get_char_invBagsUsed(self, char_i: int) -> List[dict]:
        default_type: str = "INVBAGUSED"
        src_field_name: str = f"InvBagsUsed_{char_i}"

        json_str: str = self._get_straight_field_data(
            src_field_name, default_type=default_type
        )
        inv_bags: Dict[str, int] = json.loads(json_str)

        bag_ids: List[str] = list(inv_bags)

        bag_names: List[str] = self._apply_map(
            bag_ids, item_map, "InvBag", field_unknown="bagid"
        )

        return [
            {bag_name: int(inv_bags[bag_id])}
            for bag_name, bag_id in zip(bag_names, bag_ids)
        ]

    def get_char_inventory(self, char_i: int) -> List[Dict[str, int]]:
        default_name_type: str = "INVITEMNAME"
        src_name_field_name: str = f"InventoryOrder_{char_i}"

        default_qty_type: str = "INVITEMQTY"
        src_qtty_field_name: str = f"ItemQTY_{char_i}"

        item_ids: List[str] = self._get_straight_field_data(
            src_name_field_name, default_type=default_name_type
        )
        item_qtys: List[int] = self._get_straight_field_data(
            src_qtty_field_name, default_type=default_qty_type
        )

        item_names: List[str] = self._apply_map(
            item_ids, item_map, field_unknown="itemid"
        )

        item_list: List[Dict[str, int]] = [
            {name: qty} for name, qty in zip(item_names, item_qtys)
        ]

        return item_list

    def get_char_equipment(self, char_i: int) -> List[Dict[str, int]]:
        default_equip_order_type: str = "EQUIPORDER"
        src_equip_order_field_name: str = f"EquipOrder_{char_i}"
        default_equip_qtty_type: str = "EQUIPQTTY"
        src_equip_qtty_field_name: str = f"EquipQTY_{char_i}"

        equipable_names = self._get_straight_field_data(
            src_equip_order_field_name, default_type=default_equip_order_type
        )
        equipable_counts = self._get_straight_field_data(
            src_equip_qtty_field_name, default_type=default_equip_qtty_type
        )

        equipment = self._get_armor(equipable_names, equipable_counts, char_i)
        tools = self._get_tools(equipable_names, equipable_counts, char_i)
        foods = self._get_foods(equipable_names, equipable_counts, char_i)
        return {"equipment": equipment, "tools": tools, "food": foods}

    def get_char_obols(self, char_i: int):
        raw_obol_names = self._get_straight_field_data(f"ObolEqO0_{char_i}")
        obol_map = json.loads(self._get_straight_field_data(f"ObolEqMAP_{char_i}"))

        obol_names = self._apply_map(
            raw_obol_names, obol_name_map, field_unknown="obol"
        )

        plain_obol_data = [{"name": name, "bonus": {}} for name in obol_names]

        for key in obol_map:
            plain_obol_data[int(key)]["bonus"] = obol_map[key]

        return plain_obol_data

    def get_char_statues(self, char_i: int):
        raw_statue_array = json.loads(
            self._get_straight_field_data(f"StatueLevels_{char_i}")
        )
        statue_items = [
            {"level": int(statue[0]), "progress": statue[1]}
            for statue in raw_statue_array
        ]

        return statue_items

    def get_char_cards(self, char_i: int):
        raw_cards_array = self._get_straight_field_data(f"CardEquip_{char_i}")
        cards_array = self._apply_map(
            raw_cards_array, card_equip_map, field_unknown="card"
        )

        return cards_array

    def get_char_card_set(self, char_i: int):
        raw_card_set_name = json.loads(
            self._get_straight_field_data(f"CSetEq_{char_i}")
        )
        card_effects = list(raw_card_set_name.keys())
        card_set = self._apply_map(card_effects, card_set_map, field_unknown="cardset")

        return card_set

    def get_char_skill_levels(self, char_i: int):
        raw_skill_levels = self._get_straight_field_data(f"Lv0_{char_i}")

        skill_levels = [
            int(skill_level) for skill_level in raw_skill_levels if skill_level != -1
        ]

        unmapped_indexes = list(range(len(skill_levels)))
        skill_names = self._apply_map(
            unmapped_indexes, skill_index_map, field_unknown="skill"
        )

        mapped_skills = [
            {name: level} for name, level in zip(skill_names, skill_levels)
        ]

        return mapped_skills

    def get_char_star_signs(self, char_i):
        raw_star_sign_data = self._get_straight_field_data(f"PVtStarSign_{char_i}")
        star_sign_split = raw_star_sign_data.split(",")
        for sign_index, sign in enumerate(star_sign_split):
            if sign != "":
                star_sign_split[sign_index] = sign.replace("_", "-1")
        star_sign_split = [
            int(star_sign_id) for star_sign_id in star_sign_split if sign != ""
        ]

        star_signs = [
            self._apply_map(star_sign_split, star_sign_map, field_unknown="starsignid")
        ]

        return star_signs

    def get_char_tlnt_lvls(self, char_i: int):
        raw_talents = json.loads(self._get_straight_field_data(f"SL_{char_i}"))
        talents = [int(key) for key in raw_talents.keys()]
        talent_keys = self._apply_map(talents, talent_map, field_unknown="talentid")
        mappedTalents = {
            talent_key: raw_talents[raw_key]
            for talent_key, raw_key in zip(talent_keys, raw_talents)
        }
        # regular talents

        talent_pages = self._apply_map(
            [self.get_char_class(char_i)], class_talent_map, field_unknown="classtalent"
        )[0]
        talent_pages = [
            "Savvy Basics" if key == "Savy Basics" else key for key in talent_pages
        ]
        ordered_class_talents = self._apply_map(
            talent_pages, class_talent_page_map, field_unknown="classtalentpage"
        )
        class_talents = []
        for oct in ordered_class_talents:
            class_talents += oct

        indexedTalents = {
            class_tenant: mappedTalents.get(class_tenant, "-1")
            for class_tenant in class_talents
        }

        star_talent_list = class_talent_page_map["Star Talents"]
        star_talent_indexed = {}
        counter = 0
        for star_talent in star_talent_list:
            if star_talent == "FILLER":
                star_level = 0
                star_talent += f"_{counter}"
                counter += 1

            else:
                star_level = mappedTalents.get(star_talent, -1)

            star_talent_indexed.update({star_talent: star_level})

        return {"talentLevels": indexedTalents, "starTalentLevels": star_talent_indexed}

    def get_char_atk_loadout(self, char_i: int):
        # talent attack loadout
        raw_atk_loadout = json.loads(
            self._get_straight_field_data(f"AttackLoadout_{char_i}")
        )
        # merge them all into one array

        atk_loadout = []
        for ral in raw_atk_loadout:
            atk_loadout += ral
        unmapped_loadout = [key for key in atk_loadout if key != "Null"]

        # change talent IDs to their in-game names
        mapped_loadout = self._apply_map(
            unmapped_loadout, talent_map, field_unknown="talent"
        )

        # change talent names to their readable form
        for ix, word in enumerate(mapped_loadout):
            mapped_loadout[ix] = " ".join(
                [w.capitalize() for w in word.lower().split("_")]
            )
        return mapped_loadout

    def get_char_fishing_toolkit(self, char_i: int):
        raw_tool_kit = self._get_straight_field_data(f"PVFishingToolkit_{char_i}")

        raw_bait = [int(raw_tool_kit[0])]
        raw_line = [int(raw_tool_kit[1])]

        bait = self._apply_map(raw_bait, fishing_bait_map, field_unknown="bait")
        line = self._apply_map(raw_line, fishing_line_map, field_unknown="fishline")

        return {"bait": bait, "line": line}

    def get_char_bubbles(self, char_id: int):
        raw_bubbles = json.loads(self._get_straight_field_data(f"CauldronBubbles"))[
            char_id
        ]
        bubbles = self._apply_map(raw_bubbles, large_bubble_map, field_unknown="bubble")

        return bubbles

    def get_char_anvil(self, char_id: int):
        raw_anvil = self._get_straight_field_data(f"AnvilPA_{char_id}")

        # [0-13] of rawAnvil are each anvil product
        # of each product...
        # 0 = amount to be produced (claimed)
        # 1 = amount of xp gained when claimed
        # 2 = current progress? (idk need more proof but also kinda useless)
        # 3 = ???
        anvil_products = [
            {
                "produced": int(raw_product_stats["0"]),
                "xp": int(raw_product_stats["1"]),
                "progress": float(raw_product_stats["2"]),
                "3": int(raw_product_stats["3"]),
            }
            for raw_product_stats in raw_anvil
        ]

        return anvil_products
