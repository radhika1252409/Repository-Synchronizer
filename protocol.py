import struct

# ----------------------------- OPCODES -----------------------------
FILE_CREATE = 1
FILE_MODIFY = 2
FILE_DELETE = 3

# ----------------------------- ENCODE -----------------------------
def encode(opcode, filename, filesize):
    """
    Encode the message header to send to the server.

    Header format:
    [opcode:1 byte][filename length:2 bytes][filename][filesize:8 bytes]

    For FILE_DELETE, filesize = 0 and only filename is used.
    """
    filename_bytes = filename.encode('utf-8')
    filename_len = len(filename_bytes)

    # Pack header
    header = struct.pack('!B H', opcode, filename_len) + filename_bytes
    header += struct.pack('!Q', filesize)  # 8-byte unsigned long long for filesize
    return header


# ----------------------------- DECODE -----------------------------
def decode(header_bytes):
    """
    Decode the received header bytes into opcode, filename, filesize.
    """
    # Read opcode (1 byte) and filename length (2 bytes)
    opcode = header_bytes[0]
    filename_len = struct.unpack('!H', header_bytes[1:3])[0]

    # Extract filename
    filename_bytes = header_bytes[3:3+filename_len]
    filename = filename_bytes.decode('utf-8')

    # Extract filesize (8 bytes at the end)
    filesize_bytes = header_bytes[3+filename_len:3+filename_len+8]
    filesize = struct.unpack('!Q', filesize_bytes)[0]

    return opcode, filename, filesize
