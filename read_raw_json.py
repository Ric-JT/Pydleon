import json
import requests
from template_data import cake_template
from maps.classTalentMap import class_index_map
from maps.itemMap import item_map
from maps.maps import obol_name_map


def print_hline(n: int = 100):
    print("_" * n)


def fill_characters_data(chars: list, numChars: int, fields: dict) -> list:
    for i in range(numChars):
        chars[i]["class"] = class_index_map.get(
            fields[f"CharacterClass_{i}"], "UNKNOWN"
        )
        chars[i]["money"] = fields[f"Money_{i}"]
        chars[i]["AFKtarget"] = fields[f"AFKtarget_{i}"].capitalize()
        chars[i]["currentMap"] = fields[f"CurrentMap_{i}"]
        chars[i]["npcDialogue"] = json.loads(fields[f"NPCdialogue_{i}"])
        chars[i]["timeAway"] = fields[f"PTimeAway_{i}"]
        chars[i]["instaRevives"] = fields[f"PVInstaRevives_{i}"]
        chars[i]["gender"] = (
            "Pee standing up" if fields[f"PVGender_{i}"] == 0 else "Pee seating down"
        )
        chars[i]["minigamePlays"] = fields[f"PVMinigamePlays_{i}"]

        statlist = fields[f"PVStatList_{i}"]
        columns = ["strength", "agility", "wisdom", "luck", "level"]
        for stat, value in zip(columns, statlist):
            chars[i][stat] = value

        chars[i]["POBoxUpgrades"] = fields[f"POu_{i}"]

        rawInvBagsUsed = json.loads(fields[f"InvBagsUsed_{i}"])
        bags = list(rawInvBagsUsed.keys())
        chars[i]["invBagsUsed"] = [{item_map["InvBag" + bag]: bag} for bag in bags]

        inventoryItemNames = [
            item_map.get(item_name, "UNKNOWN")
            for item_name in fields[f"InventoryOrder_{i}"]
        ]
        inventoryItemCounts = fields[f"ItemQTY_{i}"]

        chars[i]["inventory"] = [
            {item_name: int(count) if type(count) == str else count}
            for item_name, count in zip(inventoryItemNames, inventoryItemCounts)
        ]

        equipableNames = fields[f"EquipOrder_{i}"]
        equipableCounts = fields[f"EquipQTY_{i}"]

        rawEquipmentNames = [
            item_map.get(equipableNames[0][equip_name], "UNKNOWN")
            for equip_name in equipableNames[0]
            if equip_name != "length"
        ]
        rawEquipmentCounts = [
            equipableCounts[0][equip_name]
            for equip_name in equipableCounts[0]
            if equip_name != "length"
        ]
        plainEquipmentData = [
            {equip_name: count}
            for equip_name, count in zip(rawEquipmentNames, rawEquipmentCounts)
        ]
        # add upgrade stone data
        # IMm_# = players inventory (todo later as it isn't usefull for calculations)
        # EMm0_# = equips
        # EMm1_# = tools
        equipmentStoneData = json.loads(fields[f"EMm0_{i}"])

        blankData = {
            "Defence": 0,
            "WIS": 0,
            "STR": 0,
            "LUK": 0,
            "Weapon_Power": 0,
            "AGI": 0,
            "Reach": 0,
            "Upgrade_Slots_Left": 0,
            "Power": 0,
            "Speed": 0,
            "UQ1val": 0,
        }

        # add blank data to everything in the list first
        for j in range(len(plainEquipmentData)):
            plainEquipmentData[j]["stoneData"] = blankData

        # go through stone data and add any that need to be added
        keys = equipmentStoneData.keys()
        for key in keys:
            # (hacky fix) some weapon power is stored as "Weapon_Power" instead of "Power"
            # if that happens, just add "Power" with the same value
            if "Weapon_Power" in equipmentStoneData[key].keys():
                equipmentStoneData[key]["Power"] = equipmentStoneData[key][
                    "Weapon_Power"
                ]

            plainEquipmentData[int(key)]["stoneData"] = equipmentStoneData[key]

        chars[i]["equipment"] = plainEquipmentData

        rawToolNames = [
            item_map.get(equipableNames[1][tool_name], "UNKNOWN")
            for tool_name in equipableNames[1]
            if tool_name != "length"
        ]
        rawToolCounts = [
            equipableCounts[1][tool_name]
            for tool_name in equipableCounts[1]
            if tool_name != "length"
        ]

        plainToolData = [
            {tool_name: count} for tool_name, count in zip(rawToolNames, rawToolCounts)
        ]
        toolStoneData = json.loads(fields[f"EMm1_{i}"])

        # add blank data to everything in the list first
        for j in range(len(plainToolData)):
            plainToolData[j]["stoneData"] = blankData

        # go through stone data and add any that need to be added
        keys = toolStoneData.keys()
        for key in keys:
            # (hacky fix) some weapon power is stored as "Weapon_Power" instead of "Power"
            # if that happens, just add "Power" with the same value
            if "Weapon_Power" in toolStoneData[key].keys():
                toolStoneData[key]["Power"] = toolStoneData[key]["Weapon_Power"]

            plainToolData[int(key)]["stoneData"] = toolStoneData[key]

        chars[i]["tools"] = plainToolData

        rawFoodNames = [
            item_map.get(equipableNames[2][food_name], "UNKNOWN")
            for food_name in equipableNames[2]
            if food_name != "length"
        ]
        rawFoodCounts = [
            equipableCounts[2][food_name]
            for food_name in equipableCounts[2]
            if food_name != "length"
        ]
        chars[i]["food"] = [
            {food_name: count} for food_name, count in zip(rawFoodNames, rawFoodCounts)
        ]

        # obols
        obolNames = [
            obol_name_map.get(obol_name, "UNKNOWN")
            for obol_name in fields[f"ObolEqO0_{i}"]
        ]
        obolMap = json.loads(fields[f"ObolEqMAP_{i}"])
        print(obolNames)
        print(obolMap)
        plainObolData = [
            {"name": obolNames[id], "bonus": {}} for id, _ in enumerate(obolNames)
        ]
        for key in obolMap:
            plainObolData[int(key)]["bonus"] = obolMap[key]

        chars[i]["obols"] = plainObolData

    return chars


def parse_dough(dough: dict):

    numChars = len(dough["charNameData"])
    fields = dough["saveData"]
    characters = []
    for i in range(numChars):
        newCharacter = cake_template["characters"].copy()
        newCharacter["name"] = dough["charNameData"][i]
        characters += [newCharacter]
    characters = fill_characters_data(
        characters,
        numChars,
        fields,
    )

    return characters


def print_line(ids: list, values: list, prefix: str = "", separators: list = None):
    separators = [":"] * len(values) if not separators else separators
    lines = []
    line = []
    for id, value, separator in zip(ids, values, separators):
        if type(value) == dict:
            line += [prefix + f"{id}{separator}"]
            dict_lines = []
            dict_line = []
            counter = 0
            new_prefix = prefix + "\t"
            for key in value:
                if type(value[key]) == dict:
                    dict_lines += [new_prefix + " \t ".join(dict_line)]
                    dict_line = []
                else:
                    dict_line += [f"{key}{separator} {value[key]}"]
                    counter += 1
                    if counter % 5 == 0:
                        dict_lines += [new_prefix + " \t ".join(dict_line)]
                        dict_line = []
            dict_lines += [new_prefix + " \t ".join(dict_line)]

            line += ["\n".join(dict_lines)]
        elif type(value) == list and len(value):
            line += [prefix + f"{id}{separator} {type(value)} {type(value[0])}"]
            if type(value[0]) == dict or type(value[0]) != list:

                dict_lines = []
                dict_line = []
                counter = 0
                new_prefix = prefix + "\t"
                for dict_el in value:
                    dict_keys = dict_el.keys()
                    for key in dict_keys:
                        counter += 1
                        if type(dict_el[key]) == dict:
                            dict_line += [
                                new_prefix + f"{key}{separator} {dict_el[key]}"
                            ]
                            if counter % 2 == 0:
                                dict_lines += [new_prefix + " \t ".join(dict_line)]
                                dict_line = []
                        else:
                            dict_line += [f"{key}{separator} {dict_el[key]}"]
                            if counter % 2 == 0:
                                dict_lines += [new_prefix + " \t ".join(dict_line)]
                                dict_line = []
                dict_lines += [new_prefix + " \t ".join(dict_line)]

                line += ["\n".join(dict_lines)]
            elif type(value[0]) == list:
                input()

        else:
            line += [prefix + f"{id}{separator} {value}"]
        lines += line
    for line in lines:
        print(line)


def print_charachers(chars: list):
    for ch in chars:
        name, level, ch_class = ch["name"], ch["level"], ch["class"]

        columns = ["name", "class", "level"]
        line = ["", "", "lv."]
        values = [ch[column] for column in columns]
        seps = ["", "", ""]
        print_line(line, values, separators=seps)

        columns = ["strength", "agility", "wisdom"]
        line = [column.capitalize() for column in columns]
        values = [ch[column] for column in columns]
        print_line(line, values)

        columns = [
            "money",
            "AFKtarget",
            "currentMap",
            "npcDialogue",
            "timeAway",
            "instaRevives",
            "gender",
            "minigamePlays",
        ]
        for column in columns:
            print_line([column.capitalize()], [ch[column]])
        columns = [
            "POBoxUpgrades",
            "invBagsUsed",
            "inventory",
            "equipment",
            "tools",
            "food",
            "obols",
            "statueLevels",
            "cardSetEquip",
            "skillLevels",
            "starSigns",
            "talentLevels",
            "starTalentLevels",
            "fishingToolkitEquipped",
            "bubblesEquipped",
            "anvil",
        ]

        for column in columns:
            print_line([column.capitalize()], [ch[column]])

        print_hline()


if __name__ == "__main__":
    filename = "raw_data.json"
    with open(filename, "r") as fp:
        saveData = json.load(fp)

    charNameData = [
        "Mr_Piggao",
        "Miss_Piggy",
        "Piggy_Jr",
        "Sr_Puerco",
        "Grand_Pigdalf",
        "Pigolas",
        "Pigliota",
        "Ditto_Piggo",
    ]

    guildInfo = {
        "i": 31,
        "n": "Jaegerists",
        "stats": [2, 6, 5, 15, 6, 0, 5, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0],
    }
    raw_dough = {
        "charNameData": charNameData,
        "guildInfo": guildInfo,
        "saveData": saveData,
    }

    chars = parse_dough(raw_dough)
    print_charachers(chars)
