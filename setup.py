import PySimpleGUI as psg
import os
import shutil
import subprocess
import json
import itemData
import unpack
    
layout = [
    [ psg.Text("Game Directory:"), psg.Input("", key = "data"), psg.FolderBrowse() ],
    [ psg.Text("   SD Card Root:"), psg.Input("", key = "root"), psg.FolderBrowse() ],
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

        folder = "apps/love/data/" + values["button"] + " Button/"
        if (os.path.isdir(folder) == True):
            shutil.rmtree(folder)
        os.mkdir(folder)
        os.mkdir(folder + "Players/")
        os.mkdir(folder + "Stages/")
        os.mkdir(folder + "Demos/")
        os.mkdir(folder + "Basic/")
        os.mkdir(folder + "Basic/Images")
        os.mkdir(folder + "Basic/Sounds")

        nameFile = open(folder + "name.txt", "wt")
        nameFile.write(values["data"].split("/")[-2])
        nameFile.close()

        for root, dirs, files in os.walk(values["data"]):
            for file in files:
                if (file.endswith(".player") == True):
                    nameF = open(folder + "Players/playerNames.txt", "at")
                    nameF.write(file[0:-7] + "\n")
                    nameF.close()
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
                    unpack.unpack(os.path.join(root, file), folder + "Players/" + file[0:-7] + "/", "player")
                elif (file.endswith(".stage") == True):
                    nameF = open(folder + "Stages/stageNames.txt", "at")
                    nameF.write(file[0:-6] + "\n")
                    nameF.close()
                    os.mkdir(folder + "Stages/" + file[0:-6])
                    subprocess.run([ "sprite_sound_ripper.exe", file ], cwd = values["data"])
                    os.mkdir(folder + "Stages/" + file[0:-6] + "/Images")
                    os.mkdir(folder + "Stages/" + file[0:-6] + "/Sounds")
                    for r, d, f in os.walk(file[0:-6]):
                        for thing in f:
                            if (os.path.join(r, thing).split("\\")[1] == thing):
                                shutil.copyfile(file[0:-6] + "/" + thing, folder + "Stages/" + file[0:-6] + "/Images/" + thing)
                            elif (os.path.join(r, thing).split("\\")[1] == "snd"):
                                shutil.copyfile(file[0:-6] + "/snd/" + thing, folder + "Stages/" + file[0:-6] + "/Sounds/" + thing)
                    shutil.rmtree(file[0:-6])
                    unpack.unpack(os.path.join(root, file), folder + "Stages/" + file[0:-6] + "/", "stage")
                elif (file.endswith(".demo") == True):
                    nameF = open(folder + "Demos/demoNames.txt", "at")
                    nameF.write(file[0:-5] + "\n")
                    nameF.close()
                    os.mkdir(folder + "Demos/" + file[0:-5])
                    subprocess.run([ "sprite_sound_ripper.exe", file ], cwd = values["data"])
                    os.mkdir(folder + "Demos/" + file[0:-5] + "/Images")
                    os.mkdir(folder + "Demos/" + file[0:-5] + "/Sounds")
                    for r, d, f in os.walk(file[0:-5]):
                        for thing in f:
                            if (os.path.join(r, thing).split("\\")[1] == thing):
                                shutil.copyfile(file[0:-5] + "/" + thing, folder + "Demos/" + file[0:-5] + "/Images/" + thing)
                            elif (os.path.join(r, thing).split("\\")[1] == "snd"):
                                shutil.copyfile(file[0:-5] + "/snd/" + thing, folder + "Demos/" + file[0:-5] + "/Sounds/" + thing)
                    shutil.rmtree(file[0:-5])
                    unpack.unpack(os.path.join(root, file), folder + "Demos/" + file[0:-5] + "/", "demo")
                elif (file.endswith(".kgt") == True):
                    subprocess.run([ "sprite_sound_ripper.exe", file ], cwd = values["data"])
                    for r, d, f in os.walk(file[0:-4]):
                        for thing in f:
                            if (os.path.join(r, thing).split("\\")[1] == thing):
                                shutil.copyfile(file[0:-4] + "/" + thing, folder + "Basic/Images/" + thing)
                            elif (os.path.join(r, thing).split("\\")[1] == "snd"):
                                shutil.copyfile(file[0:-4] + "/snd/" + thing, folder + "Basic/Sounds/" + thing)
                    shutil.rmtree(file[0:-4])
                    unpack.unpack(os.path.join(root, file), folder + "Basic/", "basic")                  

        if (os.path.isdir(values["root"] + "apps/love/") == False):
            shutil.copytree("apps/love/", values["root"] + "apps/love/")
        else:
            if (os.path.isdir(values["root"] + folder) == True):
                shutil.rmtree(values["root"] + folder)
            shutil.copytree(folder, values["root"] + folder)
        psg.popup("Finished!")
        break

# Finish up by removing from the screen
window.close()