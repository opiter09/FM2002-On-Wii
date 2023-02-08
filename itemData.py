def signed(num):
    if (num > 30000):
        return(65536 - num)
    else:
        return(num)

def unpack(section):
    itemTypeDict = { 0: "Header", 12: "Image", 1: "Move Frame", 25: "Defense Frame", 24: "Attack Frame", 23: "Reaction Frame", 3: "Sound",
        30: "Cancel Condition", 35: "Color Modification", 4: "Object", 31: "Variable Fork", 2: "Detect Skill Fork", 22: "Detect Condition Fork",
        32: "Detect Random Fork", 36: "Detect Command Input Fork", 10: "Go To Skill", 11: "Call Skill", 9: "Loop Skill", 7: "Change Partner Place",
        20: "Change Partner Skill", 16: "Special Guage Fork", 17: "Life Guage Fork", 21: "Change Guage", 14: "BG Scenery", 26: "Time Stop",
        37: "After Image", 5: "End Skill" }
    itemType = itemTypeDict[section[0]]
    params = [int.from_bytes(section[x:(x + 1)], "little") for x in range(1, 16, 2)]
    if (itemType == "Header"):
        return({ "Skill Level": int.from_bytes(section[2:4], "little") })
    elif (itemType == "Image"):
        if (section[4] >= 0x40) and (section[4] < 0x60):
            x = True
            y = False
        elif (section[4] >= 0x80) and (section[4] < 0xA0):
            x = False
            y = True
        elif (section[4] >= 0xC0) and (section[4] < 0xE0):
            x = True
            y = True
        else:
            x = False
            y = False

        return({ "Wait Time": params[0], "X Position": signed(params[2]), "Y Position": signed(params[3]), "X Turn": x, "Y Turn": y,
            "Ignore Direction": bool(params[4]) })
    elif (itemType == "Move Frame"):
        binary = bin(params[4])[2:]
        binList = [ bool(int(binary[x])) for x in range(len(binary)) ]
        binList = binList.reversed()
        binList = binList + [ False, False, False, False, False ]
        return({ "X Move": signed(params[1]), "Y Move": signed(params[2]), "X Gravity": signed(params[0]), "Y Gravity": signed(params[3]),
            "Adds On": binList[0], "XM Stop": binList[1], "YM Stop": binList[2], "XG Stop": binList[3], "YG Stop": binList[4] })

