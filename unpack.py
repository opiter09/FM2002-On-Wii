import os
import shutil
import subprocess
import json
import itemData
from common import *

def command(section):
    name = section[0:32].decode("UTF-8", errors = "ignore").split("\0")[0]
    data = section[32:]
    params = [int.from_bytes(data[x:(x + 2)], "little") for x in range(0, len(data), 2)]

    inputs = []
    for i in range(10):
        binList = binarize(params[i + 5])
        buttons = [ "A", "B", "C", "D", "E", "F" ]
        reference = [ "A", "B", "C", "D", "E", "F" ]
        for j in range(4, 10):
            if (binList[j] == False):
                buttons.remove(reference[j - 4])

        # remember to flip when facing left
        directions = [ "Any", "None", "E", "SE", "S", "SW", "W", "NW", "N", "NE", "Anything W", "Anything N", "Anything E", "Anything S" ]
        if (len(bin(params[i + 5])) >= 6):
            theDir = directions[int("0b" + bin(params[i + 5])[-4:], 2)]
        else:
            theDir = directions[params[i + 5]]

        if (binList[12] == False) and (binList[13] == False):
            relation = "Unused"
        elif (binList[12] == False) and (binList[13] == True):
            relation = "End"
        elif (binList[12] == True) and (binList[13] == True):
            relation = "Continue"

        if (binList[14] == False) and (binList[15] == False):
            extra = "No Extra"
        elif (binList[14] == True) and (binList[15] == False):
            extra = "Mash"
        elif (binList[14] == False) and (binList[15] == True):
            extra = "Hold"
        elif (binList[14] == True) and (binList[15] == True):
            extra = "Full Circles"
        
        value = params[i + 15] # divide by 100 for Hold, since it becomes time. otherwise, it is number of pressings/beginning full circles needed.
        inputs.append([ relation, theDir, buttons, extra, value ]) 
    
    # the Time Limit does not seem to account for hold times at all. I assume intra-skill commands are like this as well.
    final = { "Name": name, "Time Limit": params[0] / 100, "Aerial Skill": params[1], "Ground Skill": params[2], "Ground Far Skill": params[3],
        "Crouching Skill": params[4] }
    for i in range(10):
        final["input" + str(i + 1)] = inputs[i]
    return(final)

def unpack(fileName, outFolder, theType):
    opening = open(fileName, "rb")
    reading = opening.read()
    opening.close()
    
    ourDict = {"scripts": []}
    scriptNum = int.from_bytes(reading[0x110:0x114], "little")
    itemSeps = []
    for i in range(scriptNum):
        section = reading[(0x114 + (i * 39)):(0x114 + ((i + 1) * 39))]
        itemSeps.append(int.from_bytes(section[32:34], "little"))
    for i in range(scriptNum):
        section = reading[(0x114 + (i * 39)):(0x114 + ((i + 1) * 39))]
        name = section[0:32].decode("UTF-8", errors = "ignore").split("\0")[0]
        ourDict["scripts"].append([name])
        if (section[35] == 1):
            ourDict["defaultScript"] = i

    itemNum = int.from_bytes(reading[(0x114 + (scriptNum * 39)):(0x114 + (scriptNum * 39) + 4)], "little")
    itemStart = 0x114 + (scriptNum * 39) + 4
    for i in range(itemNum):
        for j in range(len(itemSeps)):
            if (i == 0):
                scriptIndex = 0
                break
            elif (i < itemSeps[j]):
                scriptIndex = j - 1
                break
        section = reading[(itemStart + (i * 16)):(itemStart + ((i + 1) * 16))]
        ourDict["scripts"][scriptIndex].append(itemData.explicate(section, theType, ourDict["scripts"][scriptIndex][0]))

    imageNum = int.from_bytes(reading[(itemStart + (itemNum * 16)):(itemStart + (itemNum * 16) + 4)], "little")
    imageStart = itemStart + (itemNum * 16) + 4
    offset = imageStart
    count = -1
    for i in range(imageNum):
        width = int.from_bytes(reading[(offset + 4):(offset + 8)], "little")
        height = int.from_bytes(reading[(offset + 8):(offset + 12)], "little")
        size = int.from_bytes(reading[(offset + 16):(offset + 20)], "little")
        private = bool(reading[offset + 12])
        offset = offset + 20
        if (size != 0) or (width != 0) or (height != 0):
            count = count + 1
            if (os.path.exists(outFolder + "Images/" + str(count).zfill(4) + ".png") == True):
                os.rename(outFolder + "Images/" + str(count).zfill(4) + ".png", outFolder + "Images/" + "new_" + str(i).zfill(4) + ".png")
            if (private == False):
                if (os.path.exists(outFolder + "Images/" + "new_" + str(i).zfill(4) + ".png") == True):
                    transparency(outFolder + "Images/" + "new_" + str(i).zfill(4) + ".png")
        if (size != 0):
            offset = offset + size
        else:
            offset = offset + (width * height) 
            if (private == True):
                offset = offset + 1024
    for root, dirs, files in os.walk(outFolder + "Images/"):
        for file in files:
            if (file.startswith("new_") == True):
                try:
                    os.rename(outFolder + "Images/" + file, outFolder + "Images/" + file[4:])
                except FileExistsError as error:
                    os.remove(outFolder + "Images/" + file[4:])
                    os.rename(outFolder + "Images/" + file, outFolder + "Images/" + file[4:])
    
    soundNum = int.from_bytes(reading[(offset + (8 * 1056)):(offset + (8 * 1056) + 4)], "little")
    soundStart = offset + (8 * 1056) + 4
    offset2 = soundStart
    for i in range(soundNum):
        size = int.from_bytes(reading[(offset2 + 36):(offset2 + 40)], "little")
        offset2 = offset2 + 42 + size
        
    if (theType == "stage"):
        ourDict["bgmSound"] = int.from_bytes(reading[(offset2 + 4):(offset2 + 6)], "little")
        newFile = open(outFolder + "stageData.json", "wt")
        json.dump(ourDict, newFile, indent = "\t")
        newFile.close()
        return  
    elif (theType == "demo"):
        ourDict["bgmSound"] = int.from_bytes(reading[(offset2 + 4):(offset2 + 6)], "little")
        ourDict["duration"] = int.from_bytes(reading[(offset2 + 9):(offset2 + 13)], "little") / 100 # zero means it goes on forever.
        ourDict["buttonPressEnds"] = bool(reading[offset2 + 6])
        newFile = open(outFolder + "demoData.json", "wt")
        json.dump(ourDict, newFile, indent = "\t")
        newFile.close()
        return

    if (theType == "basic"):
        offset3 = offset2 + 4 + 0x3200 + 0x1C25
        ourDict["globalHitCooldown"] = reading[offset3] / 100
        ourDict["globalGuardCooldown"] = reading[offset3 + 1] / 100
        ourDict["globalClankCooldown"] = reading[offset3 + 2] / 100
        # those three determine the time before you can hit after hitting, guard after guarding, etc. for hitting and clanking I assume if you try
        # it no damage is dealt at all.
        ourDict["lifeBarSideNumbers"] = bool(reading[offset3 - 4])

        demoNum = len(open(outFolder[0:-6] + "Demos/demoNames.txt", "rt").read().split("\n")) - 1
        dList = ["Unused"]
        for i in range(0, demoNum * 2, 2):
            dList.append(reading[(offset3 + 3 + 0x3200 + (i * 0x80)):(offset3 + 3 + 0x3200 + ((i + 1) * 0x80))].decode("UTF-8").split("\0")[0])
        offset4 = offset3 + 0x9600 + 3
        ourDict["usedDemos"] = { 
            "Title Screen": dList[reading[offset4]],
            "1P Char Select": dList[reading[offset4 + 1]],
            "VS Char Select": dList[reading[offset4 + 2]],
            "Team Char Select": dList[reading[offset4 + 3]],
            "Game Over": dList[reading[offset4 + 4]],
            "Pre-Title Opening": dList[reading[offset4 + 5]]
        }

        binList = binarize(reading[offset4 + 8])
        ourDict["isLocked"] = binList[0]
        ourDict["usesClankCooldown"] = binList[1]
        ourDict["hasStoryMode"] = binList[2]
        ourDict["hasVersusMode"] = binList[3]
        ourDict["hasTeamMode"] = binList[4]
        ourDict["playerLifeShownOverHeads"] = binList[5]
        ourDict["titleCursorWillNotDisappear"] = binList[6]
        
        offset5 = offset4 + 12 + 0x1A08
        params = [ signed(int.from_bytes(reading[x:(x + 2)], "little")) for x in range(offset5, offset5 + 28, 2) ]
        # everything below is X then Y (or columns then rows, in one case).
        ourDict["firstCharPicturePosition"] = [ params[0], params[1] ]
        ourDict["distanceBetweenCharacters"] = [ params[2], params[3] ]
        ourDict["numberOfColumnsAndRows"] = [ params[4], params[5] ]
        ourDict["player1StartingCursorPos"] = [params[6], params[7] ]
        ourDict["player1CursorMovement"] = [ params[8], params[9] ] # the movements are offsets, how much you shift each time.
        ourDict["player2StartingCursorPos"] = [params[10], params[11] ]
        ourDict["player2CursorMovement"] = [ params[12], params[13] ]
        
        newFile = open(outFolder + "basicData.json", "wt")
        json.dump(ourDict, newFile, indent = "\t")
        newFile.close()
        return

    commandNum = int.from_bytes(reading[(offset2 + 4):(offset2 + 8)], "little")
    commandStart = offset2 + 8
    ourDict["commands"] = []
    for i in range(commandNum):
        section = reading[(commandStart + (i * 82)):(commandStart + ((i + 1) * 82))]
        ourDict["commands"].append(command(section))
    
    ourDict["reactionTable"] = []
    reactionNum = int.from_bytes(reading[(commandStart + (commandNum * 82)):(commandStart + (commandNum * 82) + 4)], "little")
    reactionStart = commandStart + (commandNum * 82) + 4
    for i in range(reactionNum):
        small = { "Reaction Skill": int.from_bytes(reading[(reactionStart + (i * 4)):(reactionStart + (i * 4) + 2)], "little"),
            "Spark Skill": int.from_bytes(reading[(reactionStart + (i * 4) + 2):(reactionStart + (i * 4) + 4)], "little") }
        # sparks are not to be Objects, but rather plain Images which get spawned as objects.
        ourDict["reactionTable"].append(small)
    
    ourDict["commonImageTable"] = []
    commonNum = int.from_bytes(reading[(reactionStart + (reactionNum * 4)):(reactionStart + (reactionNum * 4) + 4)], "little")
    commonStart = reactionStart + (reactionNum * 4) + 4
    for i in range(commonNum):
        small = { "Image ID": int.from_bytes(reading[(commonStart + (i * 6)):(commonStart + (i * 6) + 2)], "little"),
            "X Offset": signed(int.from_bytes(reading[(commonStart + (i * 6) + 2):(commonStart + (i * 6) + 4)], "little")),
            "Y Offset": signed(int.from_bytes(reading[(commonStart + (i * 6) + 4):(commonStart + (i * 6) + 6)], "little")) }
        ourDict["commonImageTable"].append(small)
    
    ourDict["age"] = int.from_bytes(reading[(commonStart + (commonNum * 6) + 0x2BBC):(commonStart + (commonNum * 6) + 0x2BBC + 4)], "little")
    genders = [ "Man", "Woman", "Both", "Neither" ]
    ourDict["gender"] = genders[reading[commonStart + (commonNum * 6) + 0x2BBC + 4]]

    basic = commonStart + (commonNum * 6) + 0x328D
    ourDict["healthBarYOffset"] = int.from_bytes(reading[basic:(basic + 2)], "little")
    ourDict["distanceBeforeFar"] = int.from_bytes(reading[(basic + 2):(basic + 4)], "little")
    ourDict["divisorForBlockingDamage"] = reading[basic + 4]
    ourDict["damageReductionStart"] = reading[basic + 5] / 100 # at this % of heath or less, you take less damage.
    ourDict["damageReductionMultiplier"] = reading[basic + 6] / 100 # in the above case, the damage is multiplied by this amount.
    ourDict["comboDamageDecrease"] = reading[basic + 7] # [this number * (# of hits - 1)] less damage than normal is dealt.
    ourDict["guardButton"] = chr(ord("A") + reading[basic + 8])
    ourDict["lifeTotal"] = int.from_bytes(reading[(basic + 9):(basic + 13)], "little")
    ourDict["specialTotal"] = int.from_bytes(reading[(basic + 13):(basic + 17)], "little") # note that 200 SP = 1 bar. this seems to be hardcoded.
    ourDict["maximumSpecialBars"] = reading[basic + 17]
    binList = binarize(reading[basic + 21])
    ourDict["autoBlock"] = binList[0]
    # this can automatically block a move approximately once every 0.5 seconds. moves blocked this way always deal 1 damage, but this does not
    # prevent effects or hitstun.
    ourDict["canBlockInTheAir"] = binList[1]
    ourDict["playableInVersusMode"] = binList[2] # this appears to not set properly? I'll probably just have it always be true.
    ourDict["hasGuardButton"] = binList[3]
    ourDict["specialIncreaseOnUserHit"] = signed(int.from_bytes(reading[(basic + 29):(basic + 31)], "little"))
    ourDict["specialIncreaseOnOpponentHit"] = signed(int.from_bytes(reading[(basic + 31):(basic + 32)], "little"))
    ourDict["startingSpecialBars"] = reading[basic + 33]

    newFile = open(outFolder + "playerData.json", "wt")
    json.dump(ourDict, newFile, indent = "\t")
    newFile.close()