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

def unpack(fileName, outFolder, playerName):
    opening = open(fileName, "rb")
    reading = opening.read()
    opening.close()
    
    ourDict = {"scripts": {}}
    scriptNum = int.from_bytes(reading[0x110:0x114], "little")
    itemSeps = []
    scriptNameList = []
    for i in range(scriptNum):
        section = reading[(0x114 + (i * 39)):(0x114 + ((i + 1) * 39))]
        itemSeps.append(int.from_bytes(section[32:34], "little"))
    for i in range(scriptNum):
        section = reading[(0x114 + (i * 39)):(0x114 + ((i + 1) * 39))]
        name = section[0:32].decode("UTF-8", errors = "ignore").split("\0")[0]
        scriptNameList.append(name)
        ourDict["scripts"][name] = []
        if (section[35] == 1):
            ourDict["defaultScript"] = name
    ourDict["orderedScripts"] = scriptNameList

    itemNum = int.from_bytes(reading[(0x114 + (scriptNum * 39)):(0x114 + (scriptNum * 39) + 4)], "little")
    itemStart = 0x114 + (scriptNum * 39) + 4
    for i in range(itemNum):
        for j in range(len(itemSeps)):
            if (i == 0):
                currentName = scriptNameList[0]
                break
            elif (i < itemSeps[j]):
                currentName = scriptNameList[j - 1]
                break
        section = reading[(itemStart + (i * 16)):(itemStart + ((i + 1) * 16))]
        ourDict["scripts"][currentName].append(itemData.unpack(section))

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

    newFile = open(outFolder + "playerData.json", "wt")
    json.dump(ourDict, newFile, indent = "\t")
    newFile.close()