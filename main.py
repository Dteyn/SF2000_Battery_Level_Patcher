import logging

# Filename of original firmware file to open
firmware_file = "bisrv-08_03.asd"

# Filename of patched firmware file to save
patched_file = "bisrv.asd"

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(message)s')

# Change battery values here
BATTERY_VALUES = {
    0x3564ec: 0xC5,  # Battery level 3 - full
    0x3564f4: 0xC0,  # Battery level 2
    0x35658c: 0xAC,  # Battery level 1
    0x356594: 0xA4,  # Battery level 0
    0x3565b0: 0x95   # Battery level -1 - near empty
}

# Stock values for sanity check
STOCK_VALUES = {
    0x3564ec: 0xBF,
    0x3564f4: 0xB7,
    0x35658c: 0xAF,
    0x356594: 0xA9,
    0x3565b0: 0xA1
}


def calculate_crc32(data):
    """
    Calculate the CRC32 value for the given data.
    """
    tab_crc32 = [(i << 24) & 0xFFFFFFFF for i in range(256)]
    for i in range(256):
        c = tab_crc32[i]
        for _ in range(8):
            c = (c << 1) ^ 0x4c11db7 if (c & (1 << 31)) else c << 1
            c &= 0xFFFFFFFF
        tab_crc32[i] = c

    c = ~0 & 0xFFFFFFFF
    for i in range(512, len(data)):
        c = (c << 8) ^ tab_crc32[((c >> 24) ^ data[i]) & 0xFF]
        c &= 0xFFFFFFFF

    return c


def sanity_check(bisrv_data):
    """
    Check if the firmware matches the expected "08.03" version.
    """
    for addr, expected_value in STOCK_VALUES.items():
        if bisrv_data[addr] != expected_value:
            logging.error("The firmware does not match the expected '08.03' version at offset %X. "
                          "Please check the offsets.", addr)
            return False
    return True


def patch_firmware(filename):
    """
    Patch the firmware file with new battery values and update its CRC32.
    """
    try:
        with open(filename, 'rb') as f:
            bisrv_data = bytearray(f.read())
        logging.info("File '%s' opened successfully.", filename)

        # Perform sanity check
        if not sanity_check(bisrv_data):
            return

        # Patch the battery values
        for addr, value in BATTERY_VALUES.items():
            bisrv_data[addr] = value
        logging.info("File patched with new battery values.")

        # Calculate new CRC32
        logging.info("Calculating new CRC32...")
        crc = calculate_crc32(bisrv_data)
        logging.info("New CRC32 value: %X", crc)

        # Update CRC32 in the bisrv_data
        bisrv_data[0x18c] = crc & 0xFF
        bisrv_data[0x18d] = (crc >> 8) & 0xFF
        bisrv_data[0x18e] = (crc >> 16) & 0xFF
        bisrv_data[0x18f] = (crc >> 24) & 0xFF

        # Write the patched data back to the file
        with open(patched_file, 'wb') as f:
            f.write(bisrv_data)
        logging.info("Patched data written back to '%s'.", patched_file)

    except FileNotFoundError:
        logging.error("File '%s' not found.", filename)
    except Exception as e:
        logging.error("An error occurred: %s", str(e))


if __name__ == "__main__":
    patch_firmware(firmware_file)
