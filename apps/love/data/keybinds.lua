binds = {}

binds.player1 = {
	["a"] = "A",
	["b"] = "B",
	["x"] = "E",
	["y"] = "F",
	["l"] = "D",
	["r"] = "D",
	["zl"] = "C",
	["zr"] = "C",
	["+"] = "Pause",
	["-"] = "Pause",
	["up"] = "Up",
	["down"] = "Down",
	["left"] = "Left",
	["right"] = "Right"
}

binds.player2 = {
	["a"] = "A",
	["b"] = "B",
	["x"] = "E",
	["y"] = "F",
	["l"] = "D",
	["r"] = "D",
	["zl"] = "C",
	["zr"] = "C",
	["+"] = "Pause",
	["-"] = "Pause",
	["up"] = "Up",
	["down"] = "Down",
	["left"] = "Left",
	["right"] = "Right"
}

for k, v in pairs(binds.player1) do
	binds.player1[k] = string.upper(string.sub(v, 1, 1)) .. string.sub(v, 2)
end
for k, v in pairs(binds.player2) do
	binds.player1[k] = string.upper(string.sub(v, 1, 1)) .. string.sub(v, 2)
end
return(binds)