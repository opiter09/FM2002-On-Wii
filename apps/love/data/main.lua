lume = require("lume")
json = require("json")

function love.load()
	main = 1
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
	pad1 = love.wiimote.getWiimotes()[1]
	pad2 = love.wiimote.getWiimotes()[2]
end

function love.update(dt)
	if (main == 1) then
		for i, v in ipairs(buttons) do
			if (pad1:isClassicDown(loveButtons[i]) == true) and (usedButtons[i] ~= "") then
				root = string.format("%s Button", v)
				main = 0
				break
			end
		end
	end
end

function love.draw()
	if (main == 1) then
		love.graphics.print("Press One Of The Following Buttons:", 200, 100)
		local vert = 125
		for i, v in ipairs(usedButtons) do
			if (v ~= "") then
				vert = vert + 25
				love.graphics.print(string.format("%s Button - %s", buttons[i], v), 250, vert)
			end
		end
		return
	end

	love.graphics.print(root, 200, 100)
	end
end
