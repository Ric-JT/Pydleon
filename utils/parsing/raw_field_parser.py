import json
import pandas as pd
from typing import List, Dict

from template_data import cake_template
from maps.itemMap import item_map
from maps.cardEquipMap import card_equip_map
from maps.talentMap import talent_map
from maps.mobMap import mob_map
from maps.cardLevelMap import card_level_map
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
    char_subclass_map,
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

    def _get_with_map_field_data(
        self, src_field_name: str, map: dict, default_type: str = None
    ) -> object:
        straight_data = self._get_straight_field_data(src_field_name, default_type)

        default_value: str = f"{UNKNOWN}-{straight_data}"
        return map.get(straight_data, default_value)

    def get_char_class(self, char_i: int) -> str:
        default_type: str = "CHARCLASS"
        src_field_name: str = f"CharacterClass_{char_i}"
        return self._get_with_map_field_data(
            src_field_name, class_index_map, default_type
        )

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
        return self._get_straight_field_data(src_field_name, default_type=default_type)

    def get_char_invBagsUsed(self, char_i: int) -> List[dict]:
        default_type: str = "INVBAGUSED"
        src_field_name: str = f"InvBagsUsed_{char_i}"

        json_str: str = self._get_straight_field_data(
            src_field_name, default_type=default_type
        )
        inv_bags: Dict[str, int] = json.loads(json_str)

        bag_ids: List[str] = list(inv_bags)
        bag_names: List[str] = [item_map[f"InvBag{bag_id}"] for bag_id in bag_ids]
        bag_values: List[int] = [inv_bags[bag_id] for bag_id in bag_ids]

        return [
            {bag_name: bag_value} for bag_name, bag_value in zip(bag_names, bag_values)
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

        item_names: List[str] = [
            item_map.get(rin, UNKNOWN + rin.upper()) for rin in item_ids
        ]

        item_list: List[Dict[str, int]] = [
            {name: qty} for name, qty in zip(item_names, item_qtys)
        ]

        return item_list
