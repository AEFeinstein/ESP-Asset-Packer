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
