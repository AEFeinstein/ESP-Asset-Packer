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
    bytes.append((img.width >> 24) & 0xFF)
    bytes.append((img.width >> 16) & 0xFF)
    bytes.append((img.width >> 8) & 0xFF)
    bytes.append((img.width >> 0) & 0xFF)
    # Append a 32 bit height
    bytes.append((img.height >> 24) & 0xFF)
    bytes.append((img.height >> 16) & 0xFF)
    bytes.append((img.height >> 8) & 0xFF)
    bytes.append((img.height >> 0) & 0xFF)

    # Iterate throught the image, packing each pixel into a bit
    byteBeingBuilt = 0
    byteLen = 0
    for x in range(img.height):
        for y in range(img.width):

            if(isPixelBlack(pixels[y, x])):
                # print("X", end="")
                byteBeingBuilt = (byteBeingBuilt << 1) | 0
            else:
                # print(" ", end="")
                byteBeingBuilt = (byteBeingBuilt << 1) | 1

            # Check if this byte is finished
            byteLen = byteLen + 1
            if(8 == byteLen):
                # If it is, append it to the output
                bytes.append(byteBeingBuilt)
                byteBeingBuilt = 0
                byteLen = 0
        # print("")

    # Iterating done, close the image
    img.close()

    # If there is still a byte being built, shift it over and append it
    if(0 != byteLen):
        byteBeingBuilt = byteBeingBuilt << (8-byteLen)
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
    totalBytes.append((len(binaryAssetList) >> 24) & 0xFF)
    totalBytes.append((len(binaryAssetList) >> 16) & 0xFF)
    totalBytes.append((len(binaryAssetList) >> 8) & 0xFF)
    totalBytes.append((len(binaryAssetList) >> 0) & 0xFF)

    # For each asset
    for asset in binaryAssetList:
        # Write the name to the index
        nameInBytes = bytearray(asset.name, 'ascii')
        totalBytes.extend(nameInBytes)
        for x in range(16-len(nameInBytes)):
            totalBytes.append(0)

        # Write the address to the index
        totalBytes.append((address >> 24) & 0xFF)
        totalBytes.append((address >> 16) & 0xFF)
        totalBytes.append((address >> 8) & 0xFF)
        totalBytes.append((address >> 0) & 0xFF)

        # Write the size to the index
        totalBytes.append((asset.packedLen >> 24) & 0xFF)
        totalBytes.append((asset.packedLen >> 16) & 0xFF)
        totalBytes.append((asset.packedLen >> 8) & 0xFF)
        totalBytes.append((asset.packedLen >> 0) & 0xFF)

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
