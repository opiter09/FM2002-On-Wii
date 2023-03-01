local lume = require("lume")
local json = require("json")
local binds = require("keybinds")
local polls = require("polling")
local chara = require("characterSelect")
local begin = require("twoDemos")
local meat = require("fighting")

local function jsonLoad(folder)
	local temp
	local temp2
	local data

	temp = string.format("%s/Basic/basicData.json", folder)
	data = love.filesystem.read(temp)
	basicData = json.decode(data)
	
	stageData = {}
	temp = string.format("%s/Stages/stageNames.txt", folder)
	temp2 = love.filesystem.read(temp)
	stageNames = lume.split(temp2, "\r\n")
	table.remove(stageNames) --with only one argument, table.remove gets rid of the last element
	for i, v in pairs(stageNames) do
		temp = string.format("%s/Stages/%s/stageData.json", folder, v)
		data = love.filesystem.read(temp)
		stageData[v] = json.decode(data)
	end
	
	playerData = {}
	temp = string.format("%s/Players/playerNames.txt", folder)
	temp2 = love.filesystem.read(temp)
	playerNames = lume.split(temp2, "\r\n")
	table.remove(playerNames)
	for i, v in pairs(playerNames) do
		temp = string.format("%s/Players/%s/playerData.json", folder, v)
		data = love.filesystem.read(temp)
		playerData[v] = json.decode(data)
	end
	
	demoData = {}
	temp = string.format("%s/Demos/demoNames.txt", folder)
	temp2 = love.filesystem.read(temp)
	demoNames = lume.split(temp2, "\r\n")
	table.remove(demoNames)
	for i, v in pairs(demoNames) do
		temp = string.format("%s/Demos/%s/demoData.json", folder, v)
		data = love.filesystem.read(temp)
		demoData[v] = json.decode(data)
	end
end

function love.load()
	location = "main"
	root = ""
	buttons = { "A", "B", "X", "Y", "L", "R", "ZL", "ZR", "Plus", "Minus" }
	loveButtons = { "a", "b", "x", "y", "l", "r", "zl", "zr", "+", "-" }
	usedButtons = {}
	for i, v in ipairs(buttons) do
		input = string.format("%s Button/name.txt", v)
		if (love.filesystem.exists(input)) then
			usedButtons[i] = love.filesystem.read(input)
		else
			usedButtons[i] = ""
		end
	end
end

function love.update(dt) -- WiiLove runs at 60 FPS
	if (string.sub(location, -4) == "Wait") then
		if (#polls.combined() == 0) then
			location = string.sub(location, 1, string.len(location) - 4)
			return
		end
	end

	if (location == "main") then
		for i, v in ipairs(buttons) do
			if (lume.find(polls.combined(), loveButtons[i]) ~= nil) and (usedButtons[i] ~= "") then
				root = string.format("%s Button", v)
				jsonLoad(root)
				location = "openingWait"
				currentStage = 1
				roundDuration = 60
				roundCount = 3
				break
			end
		end
	elseif (location == "opening") then
		if (basicData["usedDemos"]["Pre-Title Opening"] == "") then
			location = "title"
			return
		else
			begin.update(dt, "Pre-Title Opening")
		end
	elseif (location == "title") then
		begin.update(dt, "Title Screen")
	elseif (location == "options") then
		if (lume.find(polls.combined(), "zl") ~= nil) then
			currentStage = math.max(1, currentStage - (10 * dt))
		elseif (lume.find(polls.combined(), "zr") ~= nil) then
			currentStage = math.min(#stageNames, currentStage + (10 * dt))
		elseif (lume.find(polls.combined(), "l") ~= nil) then
			roundDuration = math.max(0, roundDuration - (10 * dt))
		elseif (lume.find(polls.combined(), "r") ~= nil) then
			roundDuration = math.min(99, roundDuration + (10 * dt))
		elseif (lume.find(polls.combined(), "-") ~= nil) then
			roundCount = math.max(1, roundCount - (10 * dt))
		elseif (lume.find(polls.combined(), "+") ~= nil) then
			roundCount = math.min(9, roundCount + (10 * dt))
		elseif (lume.find(polls.combined(), "a") ~= nil) then
			currentStage = stageNames[lume.round(currentStage)]
			roundDuration = lume.round(roundDuration)
			roundCount = lume.round(roundCount)
			location = "characterWait"
		end
	elseif (location == "character") then
		chara.update(dt)
	elseif (location == "fighting") then
		meat.update(dt)
	end
end

function love.draw()
	if (location == "main") then
		love.graphics.print("Press One Of The Following Buttons:", 200, 100)
		local vert = 125
		for i, v in ipairs(usedButtons) do
			if (v ~= "") then
				vert = vert + 25
				love.graphics.print(string.format("%s Button - %s", buttons[i], v), 250, vert)
			end
		end
		return
	elseif (location == "opening") then
		begin.draw("Pre-Title Opening")
	elseif (location == "title") then
		begin.draw("Title Screen")
	elseif (location == "options") then
		love.graphics.print(string.format("Stage: (ZL) %s (ZR)", stageNames[lume.round(currentStage)]), 200, 100)
		love.graphics.print(string.format("Time: (L) %s Seconds (R)", tostring(lume.round(roundDuration))), 200, 150)
		love.graphics.print(string.format("Round#: (-) %s Rounds (+)", tostring(lume.round(roundCount))), 200, 200)
		love.graphics.print("Press A To Continue", 215, 250)
	elseif (location == "character") then
		chara.draw()
	elseif (location == "fighting") then
		meat.draw()
	end
end
