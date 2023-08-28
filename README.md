# SF2000 Battery Level Patcher
This tool is designed to patch the Data Frog SF2000 `bisrv.asd` firmware file to provide a more accurate battery level representation when operating on the stock 18650 Li-Ion battery.

## Script Functionality

This Python script allows users to:

- Define Desired Voltage Levels: Easily set the desired voltage values for each of the five battery levels by modifying the VOLTAGE_LEVELS dictionary.
- Automatically Convert Voltages: The script will convert the user-defined voltage levels to the appropriate firmware values using a 50x multiplier.
- Perform a Sanity Check: Before patching, the script checks if the firmware matches the expected "08.03" version by comparing certain values at specific offsets.
- Patch the Firmware: The script will patch the `bisrv.asd` firmware file with the new battery values.
- Recalculate CRC32: After patching, the script recalculates the CRC32 to ensure firmware integrity.

## Usage

1. Download the main.py file
2. Place SF2000 firmware next to the main.py file. File should be named `bisrv-08_03.asd`
3. Edit the script to modify the `VOLTAGE_LEVELS` as needed
4. Run the script


# Background

The Data Frog SF2000 operates on a 1500mAh 18650 Li-Ion battery, which has certain characteristics that the firmware's original battery discharge curve does not account for. Specifically:

- The stock battery exhibits a pronounced drop-off in voltage when it reaches around 3.65v.
- The original firmware's battery discharge curve is designed to reach zero charge at 3.22v.

Given these characteristics, the original battery discharge curve can lead to inaccuracies in the battery meter.

## How Battery Levels Work

The firmware represents battery levels using specific values that correspond to voltage readings provided by the SAR ADC driver. When the value is above a given threshold, the # of bars displayed changes accordingly. 

There are five battery levels defined which correspond to how many bars are shown on the battery meter.

```
0xBF - 5 bars - green, full charge
0xB7 - 4 bars - green
0xAF - 3 bars - green
0xA9 - 2 bars - yellow
0xA1 - 1 bar - red, nearly empty
```

Any reading below the lowest value will display a 'low battery - charge soon' warning message which will interrupt gameplay and give the user a chance to save the game before the battery dies completely.

The values above correspond to actual voltage readings by multiplying the actual voltage by a factor of 50. For instance, a decimal value of 191 (0xBF) in the firmware corresponds to a voltage of 3.82V (191/50 = 3.82).

The firmware uses five distinct values to represent battery levels, ranging from "5 bars" (full charge) to "1 bar" (near empty). If the voltage reads less than the value corresponding to "1 bar", the device triggers a "low battery warning" on the screen.

## Problem with Stock Values

The stock battery used in the device has a distinct characteristic: it exhibits a sudden and sharp drop-off in voltage when it reaches around 3.65V. This means that once the battery voltage approaches this threshold, the device can suddenly lose power and turn off.

### Analysis of Stock Values
Let's break down the stock values provided in the firmware:

```
0xBF - 191 - 3.82v
0xB7 - 183 - 3.66v
0xAF - 175 - 3.50v
0xA9 - 169 - 3.38v
0xA1 - 161 - 3.22v
```

From the table above, we can see that the firmware's stock values are set such that the battery level drops linearly. However, the second value (3.66V) is dangerously close to the battery's cutoff voltage of 3.65V. This means that when the device reads the battery level as being at the second value (4/5 bars), the battery is on the brink of its sharp drop-off, and the device can shut down unexpectedly soon after.

### The Solution

To address this problem, we adjusted the battery discharge curve in the firmware to better match the behavior of the stock battery. Instead of the linear drop, we introduced a curve that accounts for the battery's sharp drop-off at 3.65V.

By doing so, we ensure that the battery meter provides a more accurate representation of the remaining battery life, giving users a better indication of when their device might shut down and preventing unexpected power losses.

```
5 bars - 0xC8 - 200 - 4.0v
4 bars - 0xC2 - 194 - 3.88v
3 bars - 0xBE - 190 - 3.80v
2 bars - 0xBA - 186 - 3.72v
1 bar - 0xB7 - 183 - 3.66v
```

## Other Firmware Versions Offsets

Below are the offsets for all known firmware versions as of August 28, 2023.  

Thank you to @VonMillhausen for compiling this list and to @bnister for the core research & data:

```
            0xBF        0xB7        0xAF        0xA9        0xA1
Mid-March:  0x35A8F8    0x35A900    0x35A9B0    0x35A9B8    0x35A9D4
April 20th: 0x35A954    0x35A95C    0x35AA0C    0x35AA14    0x35AA30
May 15th:   0x35C78C    0x35C794    0x35C844    0x35C84C    0x35C868
May 22nd:   0x35C790    0x35C798    0x35C848    0x35C850    0x35C86C
August 3rd: 0x3564EC    0x3564F4    0x35658C    0x356594    0x3565B0
```

# Credits

Thank you to @bnister on the Retro Handhelds Discord server for the bulk of the research on this. Without their help, this fix would not have been possible. Also, the CRC32 calculation code  was provided by @bnister as well.

Thank you to @VonMillhausen for their excellent SF2000 information repository which can be found here: https://github.com/vonmillhausen/sf2000


