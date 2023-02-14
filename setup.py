import PySimpleGUI as psg
import os
import shutil
import json
import itemData

def unpackPlayer(fileName, outFolder, playerName):
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
        
        newFile = open(outFolder + "playerData.json", "wt")
        json.dump(ourDict, newFile, indent = "\t")
        newFile.close()
        
    
layout = [
    [ psg.Text("Built Game Folder"), psg.Input("", key = "data"), psg.FolderBrowse() ],
    [ psg.Text("      SD Card Root"), psg.Input("", key = "root"), psg.FolderBrowse() ],
    [
        psg.Text("Button:"),
        psg.DropDown(values = ["A", "B", "X", "Y", "L", "R", "ZL", "ZR", "Plus", "Minus"], default_value = "A", key = "button"),
        psg.Button("Run")
    ]
]

# Create the window
window = psg.Window("", layout)

# Display and interact with the Window using an Event Loop
while True:
    event, values = window.read()
    # See if user wants to quit or window was closed
    if (event == psg.WINDOW_CLOSED) or (event == "Quit"):
        break
    elif (values == None):
        continue
    elif (values["data"] == None) or (values["root"] == None) or (values["button"] == None):
        continue
    elif (event == "Run"):
        folder = "apps/fm2k2player/data/" + values["button"] + " Button/"
        if (os.path.isdir(folder) == True):
            shutil.rmtree(folder)
        os.mkdir(folder)
        os.mkdir(folder + "Players/")
        name = open(folder + "name.txt", "wt")
        name.write(values["data"].split("/")[-1])
        name.close()
        for root, dirs, files in os.walk(values["data"]):
            for file in files:
                if (file.endswith(".player") == True):
                    os.mkdir(folder + "Players/" + file[0:-7])
                    unpackPlayer(os.path.join(root, file), folder + "Players/" + file[0:-7] + "/", file[0:-7])
        psg.popup("Finished!")
        window.close()

# Finish up by removing from the screen
window.close()