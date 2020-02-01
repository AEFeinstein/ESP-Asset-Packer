from PIL import Image
from espAssetPackerUtils import *


class pngBytesBuilder:
    def __init__(self):
        # Save the name and data
        self.bytes = bytearray()
        self.bitIdx = 0
        self.bitsBeingBuilt = 0

    def appendBit(self, bit):
        # Only append zeros or ones
        if(bit != 0):
            bit = 1
        # Append the bit
        self.bitsBeingBuilt = (self.bitsBeingBuilt << 1)
        self.bitsBeingBuilt = (self.bitsBeingBuilt | bit)
        # Check if this 32-bit val is finished
        self.bitIdx = self.bitIdx + 1
        if(32 == self.bitIdx):
            # If it is, append it to the output
            append32bits(self.bytes, self.bitsBeingBuilt)
            self.bitsBeingBuilt = 0
            self.bitIdx = 0

    def finish(self):
        # Pad the last bits out to 32 bytes
        while(self.bitIdx != 0):
            self.bitsBeingBuilt = (self.bitsBeingBuilt << 1)
            self.bitIdx = self.bitIdx + 1
            if(32 == self.bitIdx):
                # If it is, append it to the output
                append32bits(self.bytes, self.bitsBeingBuilt)
                self.bitsBeingBuilt = 0
                self.bitIdx = 0


def isPixelWhite(pix):
    sumChannel = 0
    # RGB come first
    for channel in range(3):
        sumChannel = sumChannel + pix[channel]
    sumChannel = sumChannel / 3
    return (sumChannel > 128)


def isPixelTransparent(pix):
    return (pix[3] < 128)


def processPng(dir, file):
    """This function converts a png file into 1-bit image bytes

    Arguments:
        dir {[type]} -- [description]
        file {[type]} -- [description]

    Returns:
        [type] -- [description]
    """
    # Load the image
    img = Image.open(dir + "/" + file).convert("RGBA")
    pixels = img.load()

    # Create a bytearray
    builder = pngBytesBuilder()

    # Append a 32 bit width
    append32bits(builder.bytes, img.width)
    # Append a 32 bit height
    append32bits(builder.bytes, img.height)

   # Iterate throught the image, packing each pixel into a bit
    for x in range(img.height):
        for y in range(img.width):
            pixel = pixels[y, x]
            if(isPixelTransparent(pixel)):
                builder.appendBit(0)
                builder.appendBit(1)
            elif(isPixelWhite(pixel)):
                builder.appendBit(0)
                builder.appendBit(0)
            else:
                builder.appendBit(1)

    # If there is still a 32-bit val being built, append it
    builder.finish()

    # Iterating done, close the image
    img.close()

    # Return an asset of these bytes
    return BinaryAsset(file, builder.bytes)
