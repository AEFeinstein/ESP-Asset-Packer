import os
import argparse
from PIL import Image


class BinaryAsset:
    def __init__(self, name, bytes):
        # Save the name and data
        self.name = name
        self.bytes = bytes
        # Save the actual data length
        self.packedLen = len(bytes)
        # Pad the data out to a 32 bit boundary, save that len too
        while(len(self.bytes) % 4 != 0):
            self.bytes.append(0)
        self.paddedLen = len(bytes)


def append32bits(bytes, val):
    bytes.append((val >> 0) & 0xFF)
    bytes.append((val >> 8) & 0xFF)
    bytes.append((val >> 16) & 0xFF)
    bytes.append((val >> 24) & 0xFF)


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
    byteBeingBuilt = 0
    bitIdx = 0
    for x in range(img.height):
        for y in range(img.width):

            if(not isPixelBlack(pixels[y, x])):
                byteBeingBuilt = byteBeingBuilt | (1 << (7-bitIdx))

            # Check if this byte is finished
            bitIdx = bitIdx + 1
            if(8 == bitIdx):
                # If it is, append it to the output
                bytes.append(byteBeingBuilt)
                byteBeingBuilt = 0
                bitIdx = 0

    # Iterating done, close the image
    img.close()

    # If there is still a byte being built, shift it over and append it
    if(0 != bitIdx):
        byteBeingBuilt = byteBeingBuilt << (8-bitIdx)
        bytes.append(byteBeingBuilt)

    # Return an asset of these bytes
    return BinaryAsset(file, bytes)


def processRtttl(dir, file):
    """TODO

    Arguments:
        dir {[type]} -- [description]
        file {[type]} -- [description]

    Returns:
        [type] -- [description]
    """
    return BinaryAsset(file)


def processGif(dir, file):
    """TODO

    Arguments:
        dir {[type]} -- [description]
        file {[type]} -- [description]

    Returns:
        [type] -- [description]
    """
    return BinaryAsset(file)


def processFile(dir, file):
    """This function reads a file into bytes, nothing special

    Arguments:
        dir {[type]} -- [description]
        file {[type]} -- [description]

    Returns:
        [type] -- [description]
    """
    fIn = open(dir + "/" + file, "rb")
    asset = BinaryAsset(file, fIn.read())
    fIn.close()
    return asset


def main():
    """TODO
    """

    # Parse the command line arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--directory", type=str,
                        help="Scan this directory for assets")
    parser.add_argument("-o", "--output", type=str,
                        help="Write the packed assets into this file")
    args = parser.parse_args()

    # Read all the assets into RAM
    binaryAssetList = []
    for file in os.listdir(args.directory):
        if file.endswith(".png"):
            binaryAssetList.append(processPng(args.directory, file))
        elif file.endswith(".rtl"):
            binaryAssetList.append(processRtttl(file))
        elif file.endswith(".gif"):
            binaryAssetList.append(processGif(file))
        else:
            binaryAssetList.append(processFile(file))

    # Figure out the size of the index
    address = 4 + (len(binaryAssetList) * (16 + 4 + 4))

    # Write the number of items in the index
    totalBytes = bytearray()
    append32bits(totalBytes, len(binaryAssetList))

    # For each asset
    for asset in binaryAssetList:
        # Write the name to the index
        nameInBytes = bytearray(asset.name, 'ascii')
        totalBytes.extend(nameInBytes)
        for x in range(16-len(nameInBytes)):
            totalBytes.append(0)

        # Write the address to the index
        append32bits(totalBytes, address)

        # Write the size to the index
        append32bits(totalBytes, asset.packedLen)

        # Move the address
        address = address + asset.paddedLen

    # Write the assets after the index
    for asset in binaryAssetList:
        totalBytes.extend(asset.bytes)

    # Write all the bites to the file
    fOut = open(args.output, "wb")
    fOut.write(totalBytes)
    fOut.close()

    print("Wrote assets to " + args.output)


if __name__ == "__main__":
    main()
