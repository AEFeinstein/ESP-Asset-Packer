import os
import subprocess
from sys import platform as _platform
from PIL import Image
from espAssetPackerUtils import *

def processObj(dir, file):
    # Write the given bytes to a temporary file
    objProcessorFolder = os.path.dirname(os.path.realpath(__file__)) + "/objProcessor"
    if _platform == "linux" or _platform == "linux2":
        lzcFile = objProcessorFolder + "/objProcessor"
    elif _platform == "win32" or _platform == "win64" or _platform == "cygwin":
        lzcFile = objProcessorFolder + "/objProcessor.exe"

    if not os.path.exists(lzcFile):
        os.system("make -C " + objProcessorFolder)

    # Pass the temporary file to cLzCompressor
    returned_value = subprocess.check_output(
        [lzcFile, dir + "/" + file])
    # print('returned value:', returned_value)

    # Parse the stdout from cLzCompressor
    outBytes = bytearray()

    # If you are using separated hex touples?
    for bValStr in returned_value.split():
        outBytes.append(int(bValStr, base=16))

    print( "OBJ Bytes: " + str(len(outBytes)) )

    # if you want to handle raw binary data.
    #for element in returned_value: 
    #    outBytes.append(element)

    return BinaryAsset(file, outBytes)

