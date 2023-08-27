# SF2000_Battery_Level_Patcher
A Python-based tool designed to patch the bisrv.asd firmware file for improved battery level representation.

This tool is intended as a development tool for rapid testing of battery curve values. The script patches the firmware with updated battery level values and re-calculates the CRC32.

## Usage

1. Download the main.py file
2. Place SF2000 firmware next to the main.py file. File should be named `bisrv-08_03.asd`
3. Edit the script to modify the `BATTERY_VALUES` as needed
4. Run the script


