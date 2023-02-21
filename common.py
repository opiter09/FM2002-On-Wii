from PIL import Image

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

def signed(num):
    if (num > 30000):
        return(num - 65536)
    else:
        return(num)
        
def miniSigned(num):
    if (num > 127):
        return(num - 255)
    else:
        return(num)