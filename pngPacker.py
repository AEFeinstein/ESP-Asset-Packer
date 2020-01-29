from PIL import Image
from espAssetPackerUtils import *


def isPixelBlack(pix):
    sumChannel = 0
    for channel in pix:
        sumChannel = sumChannel + channel
    sumChannel = sumChannel / len(pix)
    return (sumChannel < 128)


def processPng(dir, file):
    """This function converts a png file into 1-bit image bytes

    Arguments:
        dir {[type]} -- [description]
        file {[type]} -- [description]

    Returns:
        [type] -- [description]
    """
    # Load the image
    img = Image.open(dir + "/" + file).convert("RGB")
    pixels = img.load()

    # Create a bytearray
    bytes = bytearray()

    # Append a 32 bit width
    append32bits(bytes, img.width)
    # Append a 32 bit height
    append32bits(bytes, img.height)

    # Iterate throught the image, packing each pixel into a bit
    bitsBeingBuilt = 0
    bitIdx = 0
    for x in range(img.height):
        for y in range(img.width):

            if(not isPixelBlack(pixels[y, x])):
                bitsBeingBuilt = bitsBeingBuilt | (1 << (31-bitIdx))

            # Check if this 32-bit val is finished
            bitIdx = bitIdx + 1
            if(32 == bitIdx):
                # If it is, append it to the output
                append32bits(bytes, bitsBeingBuilt)
                bitsBeingBuilt = 0
                bitIdx = 0

    # If there is still a 32-bit val being built, append it
    if(0 != bitIdx):
        append32bits(bytes, bitsBeingBuilt)

    # Iterating done, close the image
    img.close()

    # Return an asset of these bytes
    return BinaryAsset(file, bytes)
