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

    # Second value is the number of notes
    append32bits(bytes, len(song.get("notes")))

    # Third value is the inter-note pause in ms
    append32bits(bytes, 5)

    # For each note
    for note in song.get("notes"):

        # Get and check the duration
        durationMs = round(note.get("duration"))
        if(durationMs > 65535):
            raise Exception('RTTTL Duration in ' + file +
                            ' is too long, ' + str(note))

        # Get and check the frequency, convert to clock divisor
        frequency = note.get("frequency")
        if(0 == frequency):
            # This is a rest
            clockDivisor = 0
        else:
            # Convert to ESP clock divisor
            clockDivisor = round(5000000 / (2 * frequency))
            if(clockDivisor > 65535):
                raise Exception('RTTTL note in ' + file +
                                ' is too low, ' + str(note))

        # Pack the frequency and duration into a single 32 bit value
        combinedNote = (durationMs << 16) | clockDivisor
        # Write that value to the bytes
        append32bits(bytes, combinedNote)

    # Return the new asset
    return BinaryAsset(file, bytes)
