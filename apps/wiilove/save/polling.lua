local lume = require("lume")
polls = {}

function polls.player1()
	local pressed = { "a", "b", "x", "y", "l", "r", "zl", "zr", "+", "-" }
	for i, v in ipairs(loveButtons) do
		if (love.wiimote.isClassicDown(0, v) == false) then
			lume.remove(pressed, v)
		end
	end
	return(pressed)
end

function polls.player2()
	local pressed = { "a", "b", "x", "y", "l", "r", "zl", "zr", "+", "-" }
	for i, v in ipairs(loveButtons) do
		if (love.wiimote.isClassicDown(1, v) == false) then
			lume.remove(pressed, v)
		end
	end
	return(pressed)
end

function polls.combined()
	local pressed = { "a", "b", "x", "y", "l", "r", "zl", "zr", "+", "-" }
	for i, v in ipairs(loveButtons) do
		if (love.wiimote.isClassicDown(0, v) == false) and (love.wiimote.isClassicDown(1, v) == false) then
			lume.remove(pressed, v)
		end
	end
	return(pressed)
end

return(polls)			