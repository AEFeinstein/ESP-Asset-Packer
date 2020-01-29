import os
import sys
import argparse

from espAssetPackerUtils import *

from pngPacker import processPng
from rtttlPacker import processRtttl
from gifPacker import processGif
from filePacker import processFile


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
        # Make sure the filename isn't too long for the index
        # (16 bytes, incl. null terminator)
        if(len(file) > 15):
            raise Exception('Filename too long (' + file + ')')

        # Pack the file according to it's extension
        if file.endswith(".png"):
            binaryAssetList.append(processPng(args.directory, file))
        elif file.endswith(".rtl"):
            binaryAssetList.append(processRtttl(args.directory, file))
        elif file.endswith(".gif"):
            binaryAssetList.append(processGif(args.directory, file))
        else:
            binaryAssetList.append(processFile(args.directory, file))

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
    try:
        main()
        sys.exit(0)
    except Exception as e:
        print(str(e), file=sys.stderr)
        sys.exit(-1)
