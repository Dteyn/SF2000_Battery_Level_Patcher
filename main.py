import logging

# Filename of original firmware file to open
firmware_file = "bisrv-08_03.asd"

# Filename of patched firmware file to save
patched_file = "bisrv.asd"

# Define voltage values for each battery level (user can modify these)
VOLTAGE_LEVELS = {
    "5 bars": 4.0,  # Full charge
    "4 bars": 3.92,
    "3 bars": 3.82,
    "2 bars": 3.72,
    "1 bar (red)": 3.66  # Near empty
}

# Offset addresses for each battery level - firmware 08.03
ADDRESSES = [
    0x3564ec,  # 5 bars (full charge)
    0x3564f4,  # 4 bars
    0x35658c,  # 3 bars
    0x356594,  # 2 bars (yellow)
    0x3565b0  # 1 bar (red)
]

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(message)s')


def voltage_to_value(voltage):
    """Convert voltage to the appropriate firmware value using the 50x multiplier."""
    return int(voltage * 50)


# Convert voltage levels to firmware values
BATTERY_VALUES = {addr: voltage_to_value(VOLTAGE_LEVELS[bar]) for addr, bar in zip(ADDRESSES, VOLTAGE_LEVELS)}

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
