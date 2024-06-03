# MPL3115A2 Python Driver

This repository contains a Python driver for the MPL3115A2, a precision altimeter and barometer sensor. The driver allows interfacing with the sensor using I2C to obtain pressure and temperature readings. By default, the sensor is set for max oversampling, requring at least 512 ms between samples.

## Features

- Connect to the MPL3115A2 sensor and verify communication.
- Retrieve station pressure in multiple units (millibars, inches of mercury, PSI).
- Retrieve altitude data based on factory calibrated pressure readings in multiple units (meters and feet).
- Retrieve temperature data in multiple units (degrees C, degrees F, degrees K).

## Requirements

- A micropython compatible board with the micropython environment installed and running
- MPL3115A2 sensor

## Installation

Clone this repository to your local machine:
git clone https://github.com/blueliner21/MPL3115A2Driver.git

## Constructor
The class expects a micropython initilized I2C object and the I2C bus address of the MPL3115A2 sensor. \
Example constructor:\
```python
SDA = 8
SCL = 9
ID = 0
ADDR = 0x60
i2c = I2C(ID, scl = Pin(SCL), sda = Pin(SDA), freq=100000)
Sensor = MPL3115A2(i2c, ADDR)
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
