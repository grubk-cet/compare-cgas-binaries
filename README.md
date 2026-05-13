### CGAS configurator generate function

(Thanks claude)
When the Generate button is clicked, the desktop app:

1. Calls `config.GetValues()` to obtain `(model, sensors[5], relays[5], analogOutputs[2])`.
2. Resets two counters: `filledFileCount` and `blankFileCount`.
3. Calls `GenerateBinFiles(model, sensors, relays, analogOutputs)` which:
    - **Clears the output folder** — deletes every existing file in it.
    - Generates **CGASDEV.bin** (device config).
    - Generates **CGASCH1.bin – CGASCH5.bin** (one per sensor channel).
    - Generates **CGASRL1.bin – CGASRL5.bin** (one per relay).
    - Generates **CGASAO1.bin – CGASAO2.bin** (one per analog output).
    - Generates **CGASFCFD.bin** (always a blank file).
    - Generates the **config-set label file** (zero-byte, name encodes the order options).
4. Shows a completion message with the filled/blank file counts.

In the web app, since there is no local filesystem access, all files must be generated as binary blobs in memory and then either bundled into a ZIP download or written via the [File System Access API](https://developer.mozilla.org/en-US/docs/Web/API/File_System_API) (whichever the web app already uses — match the existing pattern).

---

### Constants (from [Form_Main.cs:12–25](vscode-webview://02pad40e4r0qvvd2hn5vadm1njj0v7um6hok2oov8ephutb4f4sb/critical-environment-cgas-configurator/critical-environment-cgas-configurator-dbe48fa3673f/CGAS%20Configurator/Form_Main.cs#L12-L25))

```
MAJOR_VERSION              = 1
MINOR_VERSION              = 16
STEL_STRING_LENGTH         = 6
TWA_STRING_LENGTH          = 6
DEVICE_LOCATION_STRING_LENGTH = 33
DEVICE_NAME_STRING_LENGTH  = 33
DEVICE_STRUCT_DATASIZE     = 268
CHANNEL_STRUCT_DATASIZE    = 388
SB_MEM_STRUCT_DATASIZE     = 164
CONFIG_DATASIZE            = 8192   (all .bin files are exactly this size)
FLASH_WRITE_COUNT_DEFAULT  = 0x00000002
```

All multi-byte integers are **little-endian** (C# `BinaryWriter` default). All binary files are padded to exactly **8192 bytes** with `0xFF`.

---

### Blank binary file

Any file that is "blank" is 8192 bytes of `0xFF`. The function is called for:

- Each channel whose `sensor.IsNone()` returns true.
- Each relay whose `relay.IsNone()` returns true.
- Each analog output whose `ao.IsNone()` returns true.
- Always for `CGASFCFD.bin` (regardless of config).

Each blank file increments `blankFileCount`; each filled file increments `filledFileCount`.

---

### Checksum algorithm ([Form_Main.cs:684–697](vscode-webview://02pad40e4r0qvvd2hn5vadm1njj0v7um6hok2oov8ephutb4f4sb/critical-environment-cgas-configurator/critical-environment-cgas-configurator-dbe48fa3673f/CGAS%20Configurator/Form_Main.cs#L684-L697))

The checksum is a **simple byte sum** (not a standard CRC32 despite the name):

```
checksum = 0
for i in range(dataSize):          // dataSize = struct size minus 4 (the checksum field itself)
    checksum += buffer[i]
write checksum as int32-LE
```

Used in: `CGASDEV.bin` (dataSize = `DEVICE_STRUCT_DATASIZE - 4` = 264), `CGASCHx.bin` (dataSize = `CHANNEL_STRUCT_DATASIZE - 4` = 384), `CGASRLx.bin`, `CGASAOx.bin`.

---

### CGASDEV.bin — field layout ([Form_Main.cs:119–239](vscode-webview://02pad40e4r0qvvd2hn5vadm1njj0v7um6hok2oov8ephutb4f4sb/critical-environment-cgas-configurator/critical-environment-cgas-configurator-dbe48fa3673f/CGAS%20Configurator/Form_Main.cs#L119-L239))

Write sequentially using little-endian binary; all fields are the C# type sizes unless noted:

| Field                                                                         | Type                                                     | Notes                                                      |
| ----------------------------------------------------------------------------- | -------------------------------------------------------- | ---------------------------------------------------------- |
| `FLASH_WRITE_COUNT_DEFAULT`                                                   | int32                                                    | Always `0x00000002`                                        |
| `model.configFirmwareVersion`                                                 | per model type                                           |                                                            |
| `model.deviceModel`                                                           |                                                          |                                                            |
| `model.firmwareVersion`                                                       |                                                          |                                                            |
| `model.sensorCount`                                                           |                                                          |                                                            |
| `model.relayCount`                                                            |                                                          |                                                            |
| `model.analogOutCount`                                                        |                                                          |                                                            |
| `model.digiInputCount`                                                        |                                                          |                                                            |
| `model.warmupTime`                                                            |                                                          |                                                            |
| `model.commWarmupTime`                                                        |                                                          |                                                            |
| `model.globalEnableFlags`                                                     |                                                          |                                                            |
| `model.commMode`                                                              |                                                          |                                                            |
| `model.temperatureReadingOffset`                                              |                                                          |                                                            |
| `model.humidityReadingOffset`                                                 |                                                          |                                                            |
| `model.menuTimeout`                                                           |                                                          |                                                            |
| `model.backlightTimeout`                                                      |                                                          |                                                            |
| `(int)model.displayConfig`                                                    | int32 cast                                               |                                                            |
| `model.displayLine_1`                                                         |                                                          |                                                            |
| `model.displayLine_2`                                                         |                                                          |                                                            |
| `model.displayBrightness`                                                     |                                                          |                                                            |
| `model.displayScrollDelay`                                                    |                                                          |                                                            |
| `model.commLossTimeout`                                                       |                                                          |                                                            |
| `model.MODBUSwanID`                                                           |                                                          |                                                            |
| `model.inJigMODBUSwanID`                                                      |                                                          |                                                            |
| padding                                                                       | 2 × `0x00` bytes                                         | word alignment                                             |
| `(int)model.MODBUSconfig`                                                     | int32 cast                                               |                                                            |
| `model.overrideSeconds`                                                       |                                                          |                                                            |
| `model.passwordService`                                                       |                                                          |                                                            |
| `model.passwordTest`                                                          |                                                          |                                                            |
| `model.passwordComms`                                                         |                                                          |                                                            |
| `model.passwordAlarms`                                                        |                                                          |                                                            |
| `model.passwordConfig`                                                        |                                                          |                                                            |
| `model.passwordCalibrate`                                                     |                                                          |                                                            |
| `model.passwordDisplay`                                                       |                                                          |                                                            |
| `model.passwordAdmin`                                                         |                                                          |                                                            |
| `model.passwordHoldingReg`                                                    |                                                          |                                                            |
| `model.passwordBackdoor`                                                      |                                                          |                                                            |
| priority 1–8, each: `reqNumChannels`, `jumpToPriority`, `jumpDelay`, `access` | 4 fields × 8 priorities                                  |                                                            |
| `model.epochTime`                                                             |                                                          |                                                            |
| `model.BACnetFirmwareVersion`                                                 |                                                          |                                                            |
| padding                                                                       | 4 × `0x00` bytes                                         | word alignment                                             |
| `model.BACnetDeviceInstance`                                                  |                                                          |                                                            |
| `model.BACnetDBversion`                                                       |                                                          |                                                            |
| `model.BACnetBaud`                                                            |                                                          |                                                            |
| `model.BACnetMAC`                                                             |                                                          |                                                            |
| `model.APDUtimeout`                                                           |                                                          |                                                            |
| `model.APDUretries`                                                           |                                                          |                                                            |
| `model.maxInfoFrames`                                                         |                                                          |                                                            |
| `model.maxMaster`                                                             |                                                          |                                                            |
| `model.stelName` chars, then `0x00` padding                                   | exactly `STEL_STRING_LENGTH` (6) bytes total             |                                                            |
| `model.twaName` chars, then `0x00` padding                                    | exactly `TWA_STRING_LENGTH` (6) bytes total              |                                                            |
| `model.deviceLocation` chars, then `0x00` padding                             | exactly `DEVICE_LOCATION_STRING_LENGTH` (33) bytes total |                                                            |
| `model.deviceName` chars, then `0x00` padding                                 | exactly `DEVICE_NAME_STRING_LENGTH` (33) bytes total     |                                                            |
| padding                                                                       | 2 × `0x00` bytes                                         | word alignment                                             |
| checksum                                                                      | int32                                                    | byte-sum of first `DEVICE_STRUCT_DATASIZE - 4` = 264 bytes |
| fill                                                                          | `0xFF` repeated                                          | pad to 8192 bytes total                                    |

---

### CGASCHx.bin — field layout ([Form_Main.cs:246–382](vscode-webview://02pad40e4r0qvvd2hn5vadm1njj0v7um6hok2oov8ephutb4f4sb/critical-environment-cgas-configurator/critical-environment-cgas-configurator-dbe48fa3673f/CGAS%20Configurator/Form_Main.cs#L246-L382))

Filename: `CGASCH{channelNumber + 1}.bin` (so channel index 0 → `CGASCH1.bin`, etc.)

If `channel.IsNone()` → write blank file instead (8192 × `0xFF`).

Otherwise:

|Field|Notes|
|---|---|
|`0x02` (int32)|default write count|
|`channel.configFirmwareVersion`||
|`channel.sensorType`||
|2 × `0x00`|word alignment|
|`channel.decimals`||
|2 × `0x00`|word alignment|
|`channel.minValue`||
|`channel.calGas`||
|`channel.range`||
|`channel.zeroAD`||
|`channel.spanAD`||
|`channel.alarmSP1`||
|`channel.alarmSP2`||
|`channel.alarmSP3`||
|`channel.hysteresis`||
|`channel.faultReading`||
|`channel.minSensitivity`||
|`channel.zeroAD_overrideDrift`||
|`channel.zeroAD_faultDrift`||
|`channel.gain`||
|`channel.bias`||
|`channel.negFaultLimit`||
|`channel.zeroMask`||
|`channel.gasName` chars + `0x00` padding|exactly 7 bytes total|
|`channel.gasUnits` chars + `0x00` padding|exactly 7 bytes total|
|`channel.SSPartNumber` chars + `0x00` padding|exactly 14 bytes total|
|`channel.age`||
|`channel.maxAge`||
|12 temperature offset values||
|12 temperature compensation values||
|calibration history fields|see source lines 336–346|
|`channel.source`||
|`channel.SBID`||
|SB memory checksum|see source lines 353–354|
|`channel.enableFlag`||
|`channel.priorityMembership`||
|`channel.location` chars + padding||
|`channel.commType`||
|`0x00` padding|up to checksum position (see source lines 369–370)|
|checksum|byte-sum of first `CHANNEL_STRUCT_DATASIZE - 4` = 384 bytes|
|fill|`0xFF` to 8192 bytes|

For the fields and exact byte positions not fully enumerated here, read [Form_Main.cs lines 299–378](vscode-webview://02pad40e4r0qvvd2hn5vadm1njj0v7um6hok2oov8ephutb4f4sb/critical-environment-cgas-configurator/critical-environment-cgas-configurator-dbe48fa3673f/CGAS%20Configurator/Form_Main.cs#L299-L378) directly — they are the authoritative specification.

---

### CGASRLx.bin — field layout ([Form_Main.cs:471–559](vscode-webview://02pad40e4r0qvvd2hn5vadm1njj0v7um6hok2oov8ephutb4f4sb/critical-environment-cgas-configurator/critical-environment-cgas-configurator-dbe48fa3673f/CGAS%20Configurator/Form_Main.cs#L471-L559))

Filename: `CGASRL{relayNumber + 1}.bin`. If `relay.IsNone()` → blank file.

Key fields (read source for complete list):

|Field|Notes|
|---|---|
|`FLASH_WRITE_COUNT_DEFAULT`||
|`configFirmwareVersion`, `relaySource`||
|on/off/minOn/minOff/silence delays||
|relay logic config||
|2 × `0x00` word alignment||
|three relay config values||
|`testSeconds`||
|`location` string, 33 bytes padded||
|state parameters||
|BACnet object instance (4 bytes)||
|BACnet object name (20 × `0x00`)||
|BACnet priority nulls (16 × `0x01`)||
|BACnet priority values (16 × `0x00`)||
|BACnet polarity||
|BACnet relinquish default padding||
|checksum||
|fill to 8192 bytes with `0xFF`||

---

### CGASAOx.bin — field layout ([Form_Main.cs:388–465](vscode-webview://02pad40e4r0qvvd2hn5vadm1njj0v7um6hok2oov8ephutb4f4sb/critical-environment-cgas-configurator/critical-environment-cgas-configurator-dbe48fa3673f/CGAS%20Configurator/Form_Main.cs#L388-L465))

Filename: `CGASAO{aoNumber + 1}.bin`. If `ao.IsNone()` → blank file.

Key fields:

|Field|Notes|
|---|---|
|`FLASH_WRITE_COUNT_DEFAULT`||
|`configFirmwareVersion`||
|zero/range current settings||
|zero/range count values||
|AO logic + 2 padding bytes||
|priority||
|`location` string, 33 bytes padded||
|powerUp and commLost output settings||
|5 step values, each with padding||
|2 × `0x00` BACnet object instance padding||
|BACnet object name (22 × `0x00`)||
|BACnet priority nulls (16 × `0x01`)||
|BACnet priority values (16 × `0x00`)||
|BACnet relinquish default||
|checksum||
|fill to 8192 bytes with `0xFF`||

---

### Config-set label file (zero-byte) ([Form_Main.cs:585–677](vscode-webview://02pad40e4r0qvvd2hn5vadm1njj0v7um6hok2oov8ephutb4f4sb/critical-environment-cgas-configurator/critical-environment-cgas-configurator-dbe48fa3673f/CGAS%20Configurator/Form_Main.cs#L585-L677))

Create a file with **zero bytes of content** whose **filename** encodes the order options. Build the name as follows:

1. Start with `model.modelName` (e.g. `"CGAS-5000"`).
2. For each channel (indices 0–4), skip if `IsRHT()` or `IsNone()`:
    - If `channel.IsRemote` is true **and** NOT (model is `CGAS_SD` AND channel index is 4 / `CH5`): increment `numRemote`.
    - Otherwise (non-remote, non-RHT, non-None): append `"-{channel.sensorPartNumber}"`.
3. If `numRemote > 0`:
    - Suffix is `"RS"` for `CGAS_SC` or `CGAS_SD` models, `"R"` for all others.
    - If `numRemote == 1`: append `"-{suffix}"`.
    - If `numRemote > 1`: append `"-{numRemote}{suffix}"`.
4. If `channels[CH3].IsTemperature()`: append `"-RHT"`.
5. If `!analogOutputs[AO2].IsNone()`: append `"-2AO"`.
6. If any relay `IsRBZ()`: append `"-RBZ"`.
7. If any relay `IsRLY()`: append `"-RLY"`.
8. If `model.SplashGuardType == SplashGuard`: append `"-S"`.
9. Else if `model.SplashGuardType == SplashNose`: append `"-SN"`.

Create the file with that exact name, **write nothing to it** (0 bytes), and close it.

---

### Implementation requirements

- Implement this as a function (or set of functions) triggered by the Generate button in the web app.
- Mirror the exact function decomposition from the desktop: one function per file type, one orchestrating function.
- Track `filledFileCount` and `blankFileCount` during generation and surface both counts in the completion feedback to the user (matching the desktop's "X filled files and Y blank files generated" message).
- **Do not touch any existing web-app code** outside of: (a) the new generate functions, (b) the Generate button's click handler, and (c) any new imports those functions require.
- All binary data must be assembled using `DataView` / `Uint8Array` or equivalent, respecting little-endian byte order throughout.
- The output (10 `.bin` files + 1 zero-byte label file = 11 files total) must be delivered to the user for download — use the same mechanism the web app already uses for file output (ZIP download, File System Access API, etc.). If no such mechanism exists yet, use the [File System Access API](https://developer.mozilla.org/en-US/docs/Web/API/File_System_API) `showDirectoryPicker()` so the user can select an output folder, matching the desktop's "Output Files" folder concept.
