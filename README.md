# MPL3115A2 Micropython Driver

This repository contains a micropython driver for the MPL3115A2, a precision altimeter and barometer sensor. The driver allows interfacing with the sensor using I2C to obtain pressure and temperature readings. By default, the sensor is set for max oversampling, requring at least 512 ms between samples.

## Features

- Connect to the MPL3115A2 sensor and verify communication.
- Retrieve station pressure in multiple units (millibars, inches of mercury, PSI).
- Retrieve altitude data based on factory calibrated pressure readings in multiple units (meters and feet).
- Retrieve temperature data in multiple units (degrees C, degrees F, degrees K).

## Requirements

- A micropython compatible board with the micropython environment installed and running
- MPL3115A2 sensor

## Installation

Clone this repository to your local machine and copy over to a micropython compatible board running micropython:
git clone https://github.com/blueliner21/MPL3115A2Driver.git

## Usage

```python
from machine import I2C, Pin
from MPL3115A2Driver import MPL3115A2

# Initialize I2C
i2c = I2C(1, scl=Pin(22), sda=Pin(21))

# Create an instance of the sensor driver
sensor = MPL3115A2(i2c, ADDR=0x60)

# Get station pressure
pressure_data = sensor.GetStationPressure()
print("Station Pressure (mBar):", pressure_data['station_pressure_mBar'])
print("Station Pressure (inHg):", pressure_data['station_pressure_inHg'])
print("Station Pressure (PSI):", pressure_data['station_pressure_PSI'])

# Get altitude
altitude = sensor.GetAltitude()
print("Altitude (meters):", altitude)
```


## Methods
**ConnectAndVerify()**\
Verifies the connection to the MPL3115A2 sensor by checking the device ID. Will raise an assertion exception if chip ID does not match 0xC4

**GetStationPressure()**\
Obtains the station pressure from the sensor. Returns a dictionary with the keys:
- station_pressure_mBar
- station_pressure_inHg
- station_pressure_PSI

**GetSLP()**\
Calcualtes sea level pressure pressure based on station pressure, temperature data, and constants. Returns a dictionary with the keys:
- SLP_mBar
- SLP_inHg
- SLP_PSI

**GetAltitude()**\
Calculates and returns the altitude based on the pressure reading. Returns a dictionary with the keys:
- alt_meters
- alt_feet

**GetTemp()**\
Obtains measured temperature from sensor. Returns a dictionary with the keys:
- temp_c
- temp_f
- temp_k

## License
This project was created by [blueliner21](https://github.com/blueliner21) and is licensed under the MIT License. See the [LICENSE](https://github.com/git/git-scm.com/blob/main/MIT-LICENSE.txt) file for details.

## Contributing
Contributions are welcome! Please open an issue or submit a pull request for any changes or enhancements.
