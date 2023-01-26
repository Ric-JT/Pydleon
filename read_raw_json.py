import json
import requests
from template_data import cake_template
from maps.classTalentMap import class_index_map, class_talent_map, class_talent_page_map
from maps.itemMap import item_map
from maps.maps import (
    obol_name_map,
    card_set_map,
    skill_index_map,
    star_sign_map,
    fishing_bait_map,
    fishing_line_map,
    large_bubble_map,
)
from maps.cardEquipMap import card_equip_map
from maps.talentMap import talent_map


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

        plainObolData = [
            {"name": obolNames[id], "bonus": {}} for id, _ in enumerate(obolNames)
        ]
        for key in obolMap:
            plainObolData[int(key)]["bonus"] = obolMap[key]

        chars[i]["obols"] = plainObolData

        statueArray = json.loads(fields[f"StatueLevels_{i}"])
        statueItems = []
        for statue in statueArray:
            statueItems += [{"level": int(statue[0]), "progress": statue[1]}]

        chars[i]["statueLevels"] = statueItems

        cardsArray = [
            card_equip_map.get(card_id, "UNKNOWN")
            for card_id in fields[f"CardEquip_{i}"]
        ]

        chars[i]["cardsEquip"] = cardsArray

        rawCardSet = json.loads(fields[f"CSetEq_{i}"])
        cardSetName = rawCardSet
        chars[i]["cardSetEquip"] = [
            card_set_map.get(name, "UNKNOWN") for name in cardSetName
        ]

        rawSkillLevels = fields[f"Lv0_{i}"]
        unmappedSkillLevels = [int(skill) for skill in rawSkillLevels]
        mappedSkillLevels = {}
        for skill_index, skill_level in enumerate(unmappedSkillLevels):

            if skill_level != -1:
                mappedSkillLevels[
                    skill_index_map.get(skill_index, f"UNKNOWN-{skill_index}")
                ] = skill_level

        chars[i]["skillLevels"] = mappedSkillLevels

        rawStarSignData = fields[f"PVtStarSign_{i}"]
        starSignSplit = rawStarSignData.split(",")
        for sign_index, sign in enumerate(starSignSplit):
            starSignSplit[sign_index] = sign.replace("_", "-1")
            if sign == "":
                starSignSplit[sign_index] = "-1"

        starSign1 = star_sign_map.get(int(starSignSplit[0]), "None")
        starSign2 = star_sign_map.get(int(starSignSplit[1]), "None")
        starSignFinal = [starSign1, starSign2]
        chars[i]["starSigns"] = starSignFinal

        unmappedTalents = json.loads(fields[f"SL_{i}"])

        mappedTalents = {
            talent_map.get(int(key), "UNKNOWN"): unmappedTalents[key]
            for key in unmappedTalents.keys()
        }

        # regular talents
        talentPages = class_talent_map.get(chars[i]["class"], "UNKNOWN")

        orderedClassTalents = []

        for key in talentPages:
            orderedClassTalents += class_talent_page_map.get(
                "Savvy Basics" if key == "Savy Basics" else key, ["UNKNOWN"]
            )

        indexedTalents = {
            class_tenant: mappedTalents.get(class_tenant, "-1")
            for class_tenant in orderedClassTalents
        }

        chars[i]["talentLevels"] = indexedTalents

        starTalentList = class_talent_page_map["Star Talents"]
        starTalentIndexed = {}
        counter = 0
        for starTalent in starTalentList:
            if starTalent == "FILLER":
                starLevel = 0
                starTalent += f"_{counter}"
                counter += 1

            else:
                starLevel = mappedTalents.get(starTalent, -1)

            starTalentIndexed.update({starTalent: starLevel})

        chars[i]["starTalentLevels"] = starTalentIndexed

        # talent attack loadout
        unmappedLoadoutRaw = json.loads(fields[f"AttackLoadout_{i}"])
        # merge them all into one array
        unmappedLoadout = []

        for key in unmappedLoadoutRaw:
            unmappedLoadout += key

        # change talent IDs to their in-game names
        mappedLoadout = []
        for talentId in unmappedLoadout:
            if talentId != "Null":
                mappedLoadout += [talent_map.get(talentId, "Unknown")]

        # change talent names to their readable form
        for ix, word in enumerate(mappedLoadout):
            mappedLoadout[ix] = " ".join(
                [w.capitalize() for w in word.lower().split("_")]
            )

        chars[i]["attackLoadout"] = mappedLoadout
        chars[i]["fishingToolkitEquipped"]["bait"] = fishing_bait_map.get(
            int(fields[f"PVFishingToolkit_{i}"][0]), "UNKNOWN"
        )
        chars[i]["fishingToolkitEquipped"]["line"] = fishing_line_map.get(
            int(fields[f"PVFishingToolkit_{i}"][1]), "UNKNOWN"
        )

        charEquippedBubbles = json.loads(fields["CauldronBubbles"])[i]
        chars[i]["bubblesEquipped"] = [
            large_bubble_map.get(char_bubble, f"UNKNOWN-{char_bubble}")
            for char_bubble in charEquippedBubbles
        ]

        rawAnvil = fields[f"AnvilPA_{i}"]
        print(rawAnvil)
        # [0-13] of rawAnvil are each anvil product
        # of each product...
        # 0 = amount to be produced (claimed)
        # 1 = amount of xp gained when claimed
        # 2 = current progress? (idk need more proof but also kinda useless)
        # 3 = ???
        anvilProducts = []
        for rawProductStats in rawAnvil:
            anvilProducts += [
                {
                    "produced": int(rawProductStats["0"]),
                    "xp": int(rawProductStats["1"]),
                    "progress": float(rawProductStats["2"]),
                    "3": int(rawProductStats["3"]),
                }
            ]

        chars[i]["anvil"]["production"] = anvilProducts
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
        if id == "cardSetEquip":
            pass
        if type(value) == dict:
            line += [prefix + f"{id}{separator}"]
            dict_lines = []
            dict_line = []
            counter = 0
            new_prefix = prefix + "\t"
            for key in value:
                if type(value[key]) == dict:

                    # for key2 in value[key]:
                    #     if type(value[key][key2]) == dict:
                    dict_line += [f"{key}{separator} {value[key]}"]
                    dict_lines += [new_prefix + " \t ".join(dict_line)]
                    dict_line = []
                elif type(value[key]) == list:
                    dict_line += [f"{key}{separator}"]
                    dict_lines += [new_prefix + " \t ".join(dict_line)]
                    dict_line = []

                    new_new_prefix = new_prefix + "\t"
                    for prod_item_info in value[key]:
                        for key2 in prod_item_info:
                            dict_line += [f"{key2}{separator} {prod_item_info[key2]}"]
                        dict_lines += [new_new_prefix + " \t ".join(dict_line)]
                        dict_line = []

                else:
                    dict_line += [f"{key}{separator} {value[key]}"]
                    counter += 1
                    if counter % 5 == 0:
                        dict_lines += [new_prefix + " \t ".join(dict_line)]
                        dict_line = []
            if len(dict_line):
                dict_lines += [new_prefix + " \t ".join(dict_line)]

            line += ["\n".join(dict_lines)]
        elif type(value) == list and len(value):
            if type(value[0]) == dict:
                line += [prefix + f"{id}{separator} {type(value)} {type(value[0])}"]
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
            else:
                line += [prefix + f"{id}{separator} {value}"]

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
            "cardsEquip",
            "cardSetEquip",
            "skillLevels",
            "starSigns",
            "talentLevels",
            "starTalentLevels",
            "fishingToolkitEquipped",
            "bubblesEquipped",
            "anvil",
            "attackLoadout",
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
    print_charachers([chars[2]])
