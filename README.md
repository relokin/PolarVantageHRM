# Polar Vantage Heart Rate Monitor tool

This tool captures Bluetooth Low-Energy (BLE) Advertisements from
Polar Vantage watches. It will detect Polar Vantage watches using the
Complete Local Name advertisement unless the user provides the MAC
address of the watch. Then, it will listen for Manufacturer specific
advertisements which encode the heart rate and print the heart rate.

## Requirements

Polar Vantage watches will broadcast BLE Advertisements when selecting
a sport profile. For example, the watch will broadcast you heart rate
when `Indoor cycling` is selected. Broadcasting is enabled by default
for certain sport profiles (e.g., Indoor cycling). You can customize
and select which profiles will broadcast through the Polar Flow App
(option `HR visible to other devices`). Note that you don't need to
start recording, it's enough to select the activity (`Start training` ->
`Indoor cycling`).

The tool **will not** show the current heart rate unless you have
selected a sport profile which is configured to broadcast
measurements.

## BLE Advertisements
My Polar Vantage M (firmware ver. 5.1.8) broadcasts 3 different types
of BLE Advertisements:
* `Complete Local Name` (9): This is the model of the watch followed by
  the serial number. The tools uses this advertisement to determined
  if this is a Polar Vantage watch if the user hasn't specified the
  MAC address to listen to.
* `Flags` (1): This is a 16b field which I haven't been able to
  interpret yet, in my watch this has the value of 04. For now, the
  tool ignores it.
* `Manufacturer` (255): This is a manufacturer specific
  advertisement. In my watch it has the following format:
  ```
  6b00720872acf50200000000XX00YY
  ```
  Most bytes don't change. `YY` is the heart rate in hex. `XX` seems
  to encode some information that I have been able to interpret yet
  (e.g., the expended energy or the time interval since the last
  measurement).
