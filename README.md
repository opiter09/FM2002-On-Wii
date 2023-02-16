# FM2002-On-Wii
This is a project to allow playing Fighter Maker 2002 games on the Wii. It makes use of WiiLove, which means I am recreating a
game engine inside of a game engine.

# Credits
- All the people that figued out how to hack the Wii, made the Homebrew Channel, etc.
- The team behind Dolphin, which lets me test this
- The team behind the original Love2D (https://love2d.org/)
- Sheepolution, for their excellent primer on Love (https://www.sheepolution.com/learn/book/contents)
- HTV04, for porting Love2D to the Wii (https://github.com/HTV04/wiilove)
- rxi, for making Lume, which adds some convenient functions to Lua (https://github.com/rxi/lume), and for making json.lua,
  which allows for the importing of data in json files (https://github.com/rxi/json.lua)
- The PySimpleGUI team, for making that and PSGCompiler, so I can easily make a standalone application to unpack the game files
- hlwz5735, for making the 2D Fighter Maker Explorer, a great resource on file formats (https://github.com/hlwz5735/2dfm-exporter)
- Alethila, for making FM2Kunlock.exe, and for saving me immense amounts of time by making sprite_sound_ripper.exe
- Enterbrain, for making Fighter Maker 2002, and Alethila again, for translating it

# Disclaimer
This engine uses zero code from the original Fighter Maker 2002 exe, reverse-engineered or otherwise (mainly because I don't
know how to do any of that). As such, not only is this not illegal, but all sorts of things may be implemented incorrectly. If
you catch something like that, please let me know by creating an Issue.

