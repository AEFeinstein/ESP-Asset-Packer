from espAssetPackerUtils import *


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
