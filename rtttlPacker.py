from rtttl import parse_rtttl
from espAssetPackerUtils import *


def processRtttl(dir, file):
    """TODO

    Arguments:
        dir {[type]} -- [description]
        file {[type]} -- [description]

    Returns:
        [type] -- [description]
    """
    # Read the file as a string
    with open(dir + "/" + file, 'r') as fOpen:
        data = fOpen.read().replace('\n', '')
    # Parse the RTTTL
    song = parse_rtttl(data)

    bytes = bytearray()
    # First value is 'shouldLoop' The song should not loop
    append32bits(bytes, 0)
    # Append the number of notes
    append32bits(bytes, len(song.get("notes")))

    # For each note
    for note in song.get("notes"):
        # Append duration
        append32bits(bytes, round(note.get("duration")))
        # Append frequency
        frequency = note.get("frequency")
        if(0 == frequency):
            # This is a rest
            append32bits(bytes, 0)
        else:
            # Convert to ESP clock divisor
            append32bits(bytes, round(5000000 / (2 * frequency)))

    # Return the new asset
    return BinaryAsset(file, bytes)
