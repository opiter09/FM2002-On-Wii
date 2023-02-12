def signed(num):
    if (num > 30000):
        return(num - 65536)
    else:
        return(num)
        
def miniSigned(num):
    if (num > 127):
        return(num - 255)
    else:
        return(num)

def binarize(num):
    binary = bin(num)[2:]
    binList = [ bool(int(binary[x])) for x in range(len(binary)) ]
    binList = binList.reversed()
    binList = binList + [ False, False, False, False, False, False, False, False ]
    return(binList)
    
def variabled(num):
    binList = binarize(num)
    if (binList[6] == False) and (binList[7] == False):
        beg = "Task"
        return(beg + " " + char(ord("A") + num))
    elif (binList[6] == True) and (binList[7] == False):
        beg = "Char"
        return(beg + " " + char(ord("A") + num - 0x40))
    elif (binList[6] == False) and (binList[7] == True):
        beg = "System"
        return(beg + " " + char(ord("A") + num - 0x80))
    elif (binList[6] == True) and (binList[7] == True):
        beg = "Data"
        names = [ "X Coord.", "Y Coord.", "Map X Coord.", "Map Y Coord.", "Parent X Coord.", "Parent Y Coord.", "Time", "Round Number" ]
        return(beg + " " + names[num - 0xC0])

def unpack(section):
    itemTypeDict = { 0: "Header", 12: "Image", 1: "Move Frame", 25: "Defense Frame", 24: "Attack Frame", 23: "Reaction Frame", 3: "Sound",
        30: "Cancel Condition", 35: "Color Modification", 4: "Object", 31: "Variable Fork", 2: "Detect Skill Fork", 22: "Detect Condition Fork",
        32: "Detect Random Fork", 36: "Detect Command Input Fork", 10: "Go To Skill", 11: "Call Skill", 9: "Loop Skill", 7: "Change Partner Place",
        20: "Change Partner Skill", 16: "Special Guage Fork", 17: "Life Guage Fork", 21: "Change Guage", 14: "BG Scenery", 26: "Time Stop",
        37: "After Image", 5: "End Skill" }
    itemType = itemTypeDict[section[0]]
    params = [int.from_bytes(section[x:(x + 2)], "little") for x in range(1, 16, 2)]
    if (itemType == "Header"):
        return({ "Skill Level": int.from_bytes(section[2:4], "little") })
    elif (itemType == "Image"):
        image = section[3]
        if (section[4] >= 0x40) and (section[4] < 0x60):
            x = True
            y = False
            image = image + ((section[4] - 0x40) * 256)
        elif (section[4] >= 0x80) and (section[4] < 0xA0):
            x = False
            y = True
            image = image + ((section[4] - 0x80) * 256)
        elif (section[4] >= 0xC0) and (section[4] < 0xE0):
            x = True
            y = True
            image = image + ((section[4] - 0xC0) * 256)
        else:
            x = False
            y = False
            if (section[4] == 1):
                image = image + 256

        return({ "Image ID": image, "Wait Time": params[0], "X Position": signed(params[2]), "Y Position": signed(params[3]), "X Flip Image": x,
            "Y Flip Image": y, "Retain Direction": bool(params[4]) })
    elif (itemType == "Move Frame"):
        binList = binarize(params[4])
        return({ "X Move": signed(params[1]), "Y Move": signed(params[2]), "X Gravity": signed(params[0]), "Y Gravity": signed(params[3]),
            "Adds On": binList[0], "XM Ignore": binList[1], "YM Ignore": binList[2], "XG Ignore": binList[3], "YG Ignore": binList[4] })
    elif (itemType == "Defense Frame"):
        binList = binarize(section[10])
        return({ "X Center": signed(params[0]), "Y Center": signed(params[1]), "X Size": signed(params[2]), "Y Size": signed(params[3]),
            "DF Slot": section[9], "Collision": binList[0], "Take Damage": binList[1], "Throwable": binList[2], "Damage Mult": params[5] })
    elif (itemType == "Attack Frame"):
        binList = binarize(section[10])
        return({ "X Center": signed(params[0]), "Y Center": signed(params[1]), "X Size": signed(params[2]), "Y Size": signed(params[3]),
            "AF Slot": section[9], "Cancellable": binList[0], "Continues Damage": binList[1], "Damages If Blocked": binList[2],
            "Only Hits Blockers": binList[3], "Ignores On-Grounds": binList[4], "Ignores In-Airs": binList[5], "Unblockable": binList[6],
            "Only Hits If Continuing": binList[7], "Power": section[12] })
    elif (itemType == "Reaction Frame"):
        return({ "Standing Hit": params[0], "Crouching Hit": params[1], "Aerial Hit": params[2], "Standing Guard": params[3],
            "Crouching Guard": params[4], "Aerial Guard": params[5] })
    elif (itemType == "Sound"):
        return({ "Sound ID": int.from_bytes(section[2:4], "little") })
    elif (itemType == "Cancel Condition"):
        timing = [ "Never", "By Hit", "Always" ]
        if (section[1] <= 2):
            return({ "Checks": "Level", "Available": timing[section[1]], "Level Minimum": section[2], "Level Maximum": section[5] })
        else:
            return({ "Checks": "Skill", "Available": timing[section[1] - 8], "Special Skill": params[1] })
    elif (itemType == "Color Modification"):
        choices = [ "Revert", "Add And Half Transparent", "Add Colors Weirdly", "Full Black", "Add And Choose Opacity" ]
        return({ "Mode": choices[section[1]], "Red": miniSigned(section[2]) * (1 / 32), "Green": miniSigned(section[3]) * (1 / 32),
        "Blue": miniSigned(section[4]) * (1 / 32), "Alpha Percent": section[5] * (1 / 32) })
    elif (itemType == "Object"):
        binList = binarize(section[1])
        if (binList[0] == False) and (binList[1] == False):
            depth = "Behind"
        elif (binList[0] == True) and (binList[1] == False):
            depth = "In Front"
        elif (binList[0] == False) and (binList[1] == True):
            depth = "Chosen"

        return({ "X Offset": signed(int.from_bytes(section[8:10], "little")), "Y Offset": signed(int.from_bytes(section[10:12], "little")),
            "Object Skill": int.from_bytes(section[2:4], "little"), "Object Skill Start": section[4], "Obj Slot": section[12],
            "Ignores Jump Skill": binList[2], "Has Shadow": binList[3], "Only Moves With Parent": binList[5], "Uses Stage Coords": binList[6],
            "Depth": depth, "Z Value": section[13], "Jump Skill for Parent": params[2], "Jump Skill Duration": section[7] })
        # jump skill does not return to the original. this feature seems to basically not work, so I am going to implement it as it
        # seems like it should work: the projectile runs its script on its own, and the player simultaneously performs the jump skill,
        # then returns to default. the one thing I was able to actually figure out is that the "speed" value is actually how many items
        # of the skill are resolved before it ends
    elif (itemType == "Variable Fork"):
        binList = binarize(section[5])
        # number calculation options
        if (binList[0] == False) and (binList[1] == False):
            calc = "No Change"
        elif (binList[0] == True) and (binList[1] == False):
            calc = "Replace"
        elif (binList[0] == False) and (binList[1] == True):
            calc = "Add"
        # condition branch options
        if (binList[2] == False) and (binList[3] == False):
            branch = "No Branch"
        elif (binList[2] == True) and (binList[3] == False):
            branch = "If Same"
        elif (binList[2] == False) and (binList[3] == True):
            branch = "If Greater"
        elif (binList[2] == True) and (binList[3] == True):
            branch = "If Lesser"

        return({ "Target Variable": variabled(section[4]), "Applied Constant": params[3], "Application Type": calc,
            "Apply Variable Instead": binList[7], "Applied Variable": variabled(section[6]), "Comparison Constant": params[4],
            "Jump Condition": branch, "Jump Skill ID": params[0], "Jump Skill Start": section[3] })
    elif (itemType == "Detect Skill Fork"):
        # all these only work if they happen to the opponent as a result of the move. makes sense, but good to know.
        div = [ "Deactivated", "On Landing", "On Hit", "On Blocked Hit", "On Wall Collision", "On Non-Consecutive Hits", "On Throw" ]
        return({ "Jump Condition": div[section[1]], "Jump Skill ID": int.from_bytes(section[2:4], "little"), "Jump Skill Start": section[4] })
    elif (itemType == "Detect Condition Fork"):
        # all these check what the user is doing, of course
        div = [ "Deactivated", "If Holding Block", "If Holding Crouch", "If Holding Forwards", "If Holding Backwards", "If Holding Up",
            "If Holding Down" ]
        return({ "Jump Condition": div[section[7]], "Negate Condition": bool(section[1]), "Jump Skill ID": int.from_bytes(section[2:4], "little"),
            "Jump Skill Start": section[4] })
    elif (itemType == "Detect Random Fork"):
        return({ "RandInt Max": params[0], "Minimum For Jump": params[1], "Jump Skill ID": int.from_bytes(section[6:8], "little"),
            "Jump Skill Start": section[8] })

