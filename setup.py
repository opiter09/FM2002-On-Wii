import PySimpleGUI as psg
import os
import shutil
import subprocess
from PIL import Image
import json
import itemData
import playerUnpack       
    
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
        if (values["data"][-1] != "/"):
            values["data"] = values["data"] + "/"
        if (values["root"][-1] != "/"):
            values["root"] = values["root"] + "/"

        shutil.copyfile("FM2Kunlock.exe", values["data"] + "FM2Kunlock.exe")
        subprocess.run([ values["data"] + "FM2Kunlock.exe" ])
        shutil.copyfile("sprite_sound_ripper.exe", values["data"] + "sprite_sound_ripper.exe")

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
                    subprocess.run([ "sprite_sound_ripper.exe", file ], cwd = values["data"])
                    os.mkdir(folder + "Players/" + file[0:-7] + "/Images")
                    os.mkdir(folder + "Players/" + file[0:-7] + "/Sounds")
                    for r, d, f in os.walk(file[0:-7]):
                        for thing in f:
                            if (os.path.join(r, thing).split("\\")[1] == thing):
                                shutil.copyfile(file[0:-7] + "/" + thing, folder + "Players/" + file[0:-7] + "/Images/" + thing)
                            elif (os.path.join(r, thing).split("\\")[1] == "snd"):
                                shutil.copyfile(file[0:-7] + "/snd/" + thing, folder + "Players/" + file[0:-7] + "/Sounds/" + thing)
                    shutil.rmtree(file[0:-7])
                    playerUnpack.unpack(os.path.join(root, file), folder + "Players/" + file[0:-7] + "/", file[0:-7])

        psg.popup("Finished!")
        break

# Finish up by removing from the screen
window.close()