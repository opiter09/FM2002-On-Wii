import os
import shutil
import subprocess
from PIL import Image
import json
import itemData 

def transparency(inputFile):
    img = Image.open(inputFile)
    img = img.convert("RGBA")
    pixdata = img.load()
    color = pixdata[0, 0]
    width, height = img.size
    for y in range(height):
        for x in range(width):
            if (pixdata[x, y] == color):
                pixdata[x, y] = (255, 255, 255, 0)
    img.save(inputFile, "PNG")

def binarize(num):
    binary = bin(num)[2:]
    binList = [ bool(int(binary[x])) for x in range(len(binary)) ]
    binList.reverse()
    binList = binList + ([False] * 16)
    return(binList)

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

def unpack(fileName, outFolder, playerName):
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
        ourDict["scripts"][scriptIndex].append(itemData.unpack(section))

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
                os.rename(outFolder + "Images/" + file, outFolder + "Images/" + file[4:])
    
    soundNum = int.from_bytes(reading[(offset + (8 * 1056)):(offset + (8 * 1056) + 4)], "little")
    soundStart = offset + (8 * 1056) + 4
    offset2 = soundStart
    for i in range(soundNum):
        size = int.from_bytes(reading[(offset2 + 36):(offset2 + 40)], "little")
        offset2 = offset2 + 42 + size
    
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
        # sparks are (probably) meant to be skills that spawn objects
        ourDict["reactionTable"].append(small)
    
    newFile = open(outFolder + "playerData.json", "wt")
    json.dump(ourDict, newFile, indent = "\t")
    newFile.close()