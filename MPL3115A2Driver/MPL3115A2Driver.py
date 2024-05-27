from machine import Pin, I2C
import time
import math

## MPL3115A2 Registers
_STATUS = 0x00
_OUT_P_MSB = 0x01
_OUT_P_CSB = 0x02
_OUT_P_LSB = 0x03
_OUT_T_MSB = 0x04
_OUT_T_LSB = 0x05
_WHO_AM_I = 0x0C
_PT_DATA_CFG = 0x13
_BAR_IN_MSB = 0x14
_BAR_IN_LSB = 0x15
_CTRL_REG1 = 0x26

##MPL3115A2 Macros
_device_id = 0xC4

#Constants
_STATION_ALTITUDE = 1723 #meters
_g = 9.80665 #Gravitational acceleration 
_Rd = 287.05 #Specific gas constant for dry air 


class MPL3115A2:

    def __init__(self, i2c: I2C, ADDR: int):
        self.i2c = i2c
        self.ADDR = ADDR
        self.ConnectAndVerify()
    
    def ConnectAndVerify(self): #ToDo: Connect and verify should be in a try loop
        if  (self.i2c.readfrom_mem(self.ADDR,_WHO_AM_I,1))[0] == _device_id:
            print("Comms verified. Chip model number confirmed")
        else:
            print("No Comms or Bad Chip") #ToDo: This should raise an exception 
    
    def TestDeviceAltimeter(self):
        self.i2c.writeto(self.ADDR,bytearray([_PT_DATA_CFG,0x07])) ##Enable Data Flags
        self.i2c.writeto(self.ADDR,bytearray([_CTRL_REG1,0xB9])) ##Altimeter Mode, 128 OSR, Active with aquisition every 1 second         
        STA = self.i2c.readfrom_mem(self.ADDR,0x00,1) 
        while(not((STA[0]) & (0x08))): ##Check to see if measurement is completed
            #time.sleep_ms(500)
            STA = self.i2c.readfrom_mem(self.ADDR,0x00,1)
        self.i2c.writeto(self.ADDR,bytes([0x04]),False)
        data = self.i2c.readfrom(0x60,2)
        MSB = data[0]
        LSB = data[1]
        temp = (MSB<<8) | (LSB)
        temp = temp>>4
        temp = temp/16.0
        print(temp)
        self.i2c.writeto(self.ADDR,bytearray([_CTRL_REG1,0x38])) ##Altimeter Mode, 128 OSR, On Standby

    def GetStationPressure(self):
        """Obtain Station Pressure from MPL3115A2. Return a dict of station pressure in millibars, inHG, and PSI
        Return Dict Keys are: 'station_pressure_mBar', 'station_pressure_inHg', 'station_pressure_PSI'
        """
        self.i2c.writeto(self.ADDR,bytearray([_PT_DATA_CFG,0x07])) ##Enable Data Flags
        self.i2c.writeto(self.ADDR,bytearray([_CTRL_REG1,0x39])) ##Barometer Mode, 128 OSR, Active with aquisition every 1 second         
        STA = self.i2c.readfrom_mem(self.ADDR,0x00,1) 
        while(not((STA[0]) & (0x08))): ##Check to see if measurement is completed
            #time.sleep_ms(10)
            STA = self.i2c.readfrom_mem(self.ADDR,0x00,1)
        
        data = self.i2c.readfrom_mem(0x60,_OUT_P_MSB,3) #Get three bytes starting at _OUT_P_MSB register
        MSB = data[0]
        CSB = data[1]
        LSB = data[2]
        station_pressure_Pa = ((MSB<<24) | (CSB<<16) | (LSB<<8)) / 16384.0
        station_pressure_mBar = station_pressure_Pa/100
        station_pressure_inHg = station_pressure_Pa/3386
        station_pressure_PSI = station_pressure_Pa/6895
        return{"station_pressure_mBar": station_pressure_mBar, "station_pressure_inHg": station_pressure_inHg,"station_pressure_PSI": station_pressure_PSI}
    
        

    def GetSLP(self):
        """
        Calculate Sea Level Pressure from MPL3115A2 station pressure. Return a dict of SLP in millibars, inHG, and PSI.
        Station pressure is read from sensor along with temperature. SLP is approximated by:
        SLP = Station_Pressure * exp((_g*_STA_ALTITUDE)/(_Rd*tempK))
        Return Dict Keys: 'SLP_mBar', 'SLP_inHg', SLP_PSI'
        """
        self.i2c.writeto(self.ADDR,bytearray([_PT_DATA_CFG,0x07])) ##Enable Data Flags
        self.i2c.writeto(self.ADDR,bytearray([_CTRL_REG1,0x39])) ##Barometer Mode, 128 OSR, Active with aquisition every 1 second         
        STA = self.i2c.readfrom_mem(self.ADDR,0x00,1) 
        while(not((STA[0]) & (0x08))): ##Check to see if measurement is completed
            #time.sleep_ms(500)
            STA = self.i2c.readfrom_mem(self.ADDR,0x00,1)
        
        data = self.i2c.readfrom_mem(0x60,_OUT_P_MSB,5) #Get three bytes starting at _OUT_P_MSB register
        Press_MSB = data[0]
        Press_CSB = data[1]
        Press_LSB = data[2]
        Temp_MSB = data[3]
        Temp_LSB = data[4]
        station_pressure_Pa = ((Press_MSB<<24) | (Press_CSB<<16) | (Press_LSB<<8)) / 16384.0
        station_pressure_mBar = station_pressure_Pa/100
        temp_c = ((Temp_MSB << 8) | Temp_LSB) / 256.0
        temp_k = temp_c + 273.15
        exp = ((_g*_STATION_ALTITUDE)/(_Rd*temp_k))
        SLP_mBar = station_pressure_mBar * math.exp(exp)
        SLP_inHg = SLP_mBar/33.864
        SLP_PSI = SLP_mBar/68.948
        return{"SLP_mBar": SLP_mBar, "SLP_inHg":SLP_inHg, "SLP_PSI": SLP_PSI}
    
    def GetAltitude(self):
        """
        Obtain SLP adjusted altitude. Return a dict of altitudes in meters, and feet
        Return Dict Keys: 'alt_meters', 'alt_feet'
        """
        self.i2c.writeto(self.ADDR,bytearray([_PT_DATA_CFG,0x07])) ##Enable Data Flags
        self.i2c.writeto(self.ADDR,bytearray([_CTRL_REG1,0xB9])) ##Altimeter Mode, 128 OSR, Active with aquisition every 1 second         
        STA = self.i2c.readfrom_mem(self.ADDR,0x00,1) 
        while(not((STA[0]) & (0x08))): ##Check to see if measurement is completed
            #time.sleep_ms(500)
            STA = self.i2c.readfrom_mem(self.ADDR,0x00,1)

        
        data = self.i2c.readfrom_mem(0x60,_OUT_P_MSB,3) #Get three bytes starting at _OUT_P_MSB register
        ALT_MSB = data[0]
        ALT_CSB = data[1]
        ALT_LSB = data[2]
        
        station_ALT_meters = ((ALT_MSB<<24) | (ALT_CSB<<16) | (ALT_LSB<<8)) / 65536.0    
        station_ALT_feet = station_ALT_meters * 3.281
        
        return{"alt_meters": station_ALT_meters, "alt_feet":station_ALT_feet}

    def GetTemp(self):
        """
        Obtain temperature data. Return a dict of temperatures in degrees_c, degrees_f, and degrees_k
        Return Dict Keys: 'temp_c', 'temp_f', 'temp_k'
        """
        self.i2c.writeto(self.ADDR,bytearray([_PT_DATA_CFG,0x07])) ##Enable Data Flags
        self.i2c.writeto(self.ADDR,bytearray([_CTRL_REG1,0x39])) ##Barometer Mode, 128 OSR, Active with aquisition every 1 second         
        STA = self.i2c.readfrom_mem(self.ADDR,0x00,1) 
        while(not((STA[0]) & (0x08))): ##Check to see if measurement is completed
            #time.sleep_ms(500)
            STA = self.i2c.readfrom_mem(self.ADDR,0x00,1)
        
        data = self.i2c.readfrom_mem(0x60,_OUT_T_MSB,2) 
        Temp_MSB = data[0]
        Temp_LSB = data[1]
        temp_c = ((Temp_MSB << 8) | Temp_LSB) / 256.0
        temp_f = (temp_c * (9/5)) + 32
        temp_k = temp_c + 273.15
        
        return{"temp_c": temp_c, "temp_f":temp_f, "temp_k": temp_k}  
        
 



if __name__ == "__main__":
    SDA = 8
    SCL = 9
    ID = 0
    ADDR = 0x60
    i2c = I2C(ID, scl = Pin(SCL), sda = Pin(SDA), freq=100000)
    altimeter = MPL3115A2(i2c, ADDR)
    for i in range(10):
        pressure = altimeter.GetSLP()
        altitude = altimeter.GetAltitude()
        temp = altimeter.GetTemp()
        print(f'Pressure: {pressure["SLP_inHg"]:.2f} inHg Altitude: {altitude["alt_meters"]:.2f} meters Temp: {temp["temp_f"]:.2f} degrees F')
        
    
    

    