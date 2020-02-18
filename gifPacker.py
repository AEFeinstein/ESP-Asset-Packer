import subprocess
import os
from espAssetPackerUtils import *
from PIL import Image, ImageSequence


def isBlackPixel(pix):
    sumChannel = 0
    for channel in pix:
        sumChannel = sumChannel + channel
    return (sumChannel < (255 * len(pix)) / 2)


def frameToBytes(frame):
    # Start with blank everything
    frameBytes = bytearray()
    byteInProgress = 0
    bitsAdded = 0
    pix = frame.load()

    # For each pixel
    for y in range(frame.height):
        for x in range(frame.width):

            # Increment bits added
            if(isBlackPixel(pix[x, y])):
                byteInProgress = (byteInProgress << 1)
                # print(" ", end="")
            else:
                byteInProgress = (byteInProgress << 1) | 1
                # print("X", end="")
            bitsAdded = bitsAdded + 1

            # If 8 bits were added
            if(bitsAdded == 8):
                frameBytes.append(byteInProgress)
                byteInProgress = 0
                bitsAdded = 0
        # print("")
    return frameBytes


def diffFrame(lastFrame, currFrame):
    frameDiff = bytearray()
    for i in range(min(len(lastFrame), len(currFrame))):
        frameDiff.append(currFrame[i] ^ lastFrame[i])
    return frameDiff


def lzCompressBytes(bytes):

    # Write the given bytes to a temporary file
    tmpFileName = "tmp.bin"
    outFile = open(tmpFileName, "wb")
    outFile.write(bytes)
    outFile.close()

    lzcFolder = os.path.dirname(os.path.realpath(__file__)) + "/cLzCompressor"
    lzcFile = lzcFolder + "/cLzCompressor"
    if not os.path.exists(lzcFile):
        os.system("make -C " + lzcFolder)

    # Pass the temporary file to cLzCompressor
    returned_value = subprocess.check_output(
        [lzcFile, tmpFileName])
    # print('returned value:', returned_value)

    # Parse the stdout from cLzCompressor
    compressedBytes = bytearray()
    for bValStr in returned_value.split():
        compressedBytes.append(int(bValStr, base=16))

    # Delete the temporary file
    os.remove(tmpFileName)

    # Return the compressed bytes
    return compressedBytes


def processGif(dir, file):
    """TODO

    Arguments:
        dir {[type]} -- [description]
        file {[type]} -- [description]

    Returns:
        [type] -- [description]
    """
    bytes = bytearray()

    currentFrame = []
    prevFrame = []
    for frame in ImageSequence.Iterator(Image.open(dir + "/" + file)):
        # Get the bytes from this image
        currentFrame = frameToBytes(frame.convert('RGB'))

        # If this is the first frame
        if len(prevFrame) == 0:

            # write some metadata
            append32bits(bytes, frame.width)
            append32bits(bytes, frame.height)
            append32bits(bytes, frame.n_frames)
            duration = frame.info.get("duration")
            if None is duration:
                duration = 0
            elif 0 == duration:
                duration = 100
            append32bits(bytes, duration)

            # write the first frame
            compressedBytes = lzCompressBytes(currentFrame)
            append32bits(bytes, len(compressedBytes))
            bytes.extend(compressedBytes)
            while(len(bytes) % 4 != 0):
                bytes.append(0)
        else:
            # Just write the difference
            compressedBytes = lzCompressBytes(
                diffFrame(prevFrame, currentFrame))
            append32bits(bytes, len(compressedBytes))
            bytes.extend(compressedBytes)
            while(len(bytes) % 4 != 0):
                bytes.append(0)

        prevFrame = currentFrame

    return BinaryAsset(file, bytes)
