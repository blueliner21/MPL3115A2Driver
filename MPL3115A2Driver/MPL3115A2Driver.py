from machine import Pin, I2C
import time
import math

## MPL3115A2 Registers
_STATUS = 0x00
_OUT_P_MSB = 0x01
_OUT_P_CSB = 0x02
_OUT_P_LSB = 0x03
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


class MPL3115A2_Altimeter:

    def __init__(self, i2c: I2C, ADDR: int):
        self.i2c = i2c
        self.ADDR = ADDR
        self.ConnectAndVerify()
    
    def ConnectAndVerify(self): #ToDo: Connect and verify should be in a try loop
        #device_id_byte_array = bytearray(device_id)
        if  (self.i2c.readfrom_mem(self.ADDR,_WHO_AM_I,1))[0] == _device_id:
            print("Comms verified. Chip model number confirmed")
        else:
            print("No Comms or Bad Chip") #ToDo: This should raise an exception 
    
    def TestDeviceAltimeter(self):
        self.i2c.writeto(self.ADDR,bytearray([_PT_DATA_CFG,0x07])) ##Enable Data Flags
        self.i2c.writeto(self.ADDR,bytearray([_CTRL_REG1,0xB9])) ##Altimeter Mode, 128 OSR, Active with aquisition every 1 second         
        STA = self.i2c.readfrom_mem(self.ADDR,0x00,1) 
        while(not((STA[0]) & (0x08))): ##Check to see if measurement is completed
            time.sleep_ms(500)
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
        """Obtain Station Pressure from MPL3115A2. Return a tuple of station pressure in millibars, inHG, and PSI"""
        self.i2c.writeto(self.ADDR,bytearray([_PT_DATA_CFG,0x07])) ##Enable Data Flags
        self.i2c.writeto(self.ADDR,bytearray([_CTRL_REG1,0x39])) ##Barometer Mode, 128 OSR, Active with aquisition every 1 second         
        STA = self.i2c.readfrom_mem(self.ADDR,0x00,1) 
        while(not((STA[0]) & (0x08))): ##Check to see if measurement is completed
            time.sleep_ms(500)
            STA = self.i2c.readfrom_mem(self.ADDR,0x00,1)
        
        data = self.i2c.readfrom_mem(0x60,_OUT_P_MSB,3) #Get three bytes starting at _OUT_P_MSB register
        MSB = data[0]
        CSB = data[1]
        LSB = data[2]
        station_pressure = (MSB<<16) | (CSB<<8) | (LSB)
        station_pressure = station_pressure >> 4
        station_pressure = station_pressure/4
        station_pressure_mBar = station_pressure/100
        station_pressure_inHG = station_pressure/3386
        station_pressure_PSI = station_pressure/6895
        return(station_pressure_mBar,station_pressure_inHG,station_pressure_PSI)
        

    def GetSLP(self):
        """
        Calculate Sea Level Pressure from MPL3115A2 station pressure. Return a tuple of SLP in millibars, inHG, and PSI.
        Station pressure is read from sensor along with temperature. SLP is approximated by:
        SLP = Station_Pressure * exp((_g*_STA_ALTITUDE)/(_Rd*tempK))
        """
        self.i2c.writeto(self.ADDR,bytearray([_PT_DATA_CFG,0x07])) ##Enable Data Flags
        self.i2c.writeto(self.ADDR,bytearray([_CTRL_REG1,0x39])) ##Barometer Mode, 128 OSR, Active with aquisition every 1 second         
        STA = self.i2c.readfrom_mem(self.ADDR,0x00,1) 
        while(not((STA[0]) & (0x08))): ##Check to see if measurement is completed
            time.sleep_ms(500)
            STA = self.i2c.readfrom_mem(self.ADDR,0x00,1)
        
        data = self.i2c.readfrom_mem(0x60,_OUT_P_MSB,5) #Get three bytes starting at _OUT_P_MSB register
        Press_MSB = data[0]
        Press_CSB = data[1]
        Press_LSB = data[2]
        Temp_MSB = data[3]
        Temp_LSB = data[4]
        station_pressure = (Press_MSB<<16) | (Press_CSB<<8) | (Press_LSB)
        station_pressure = station_pressure >> 4
        station_pressure = station_pressure/4
        station_pressure_mBar = station_pressure/100
        temp_c = (Temp_MSB<<8) | (Temp_LSB)
        temp_c = temp_c>>4
        temp_c = temp_c/16.0
        temp_k = temp_c + 273.15
        exp = ((_g*_STATION_ALTITUDE)/(_Rd*temp_k))
        SLP_mB = station_pressure_mBar * math.exp(exp)
        SLP_inHG = SLP_mB/33.864
        SLP_PSI = SLP_mB/68.948
        return(SLP_mB,SLP_inHG,SLP_PSI)
    
    def GetAltitude(self):
        """
        Obtain SLP adjusted altitude
        """
        
        # SLP = self.GetSLP() #We need to get SLP to calibrate altimeter against
        
        # SLP_Pa = int((SLP[0] * 100)/2) #SLP[0] is mBar SLP. Altimeter adjustment needs SLP in pascals, mB *100. The two regesisters hold pressure in 2 Pa units, SLP_Pa/2
        # SLP_Pa_MSB = (SLP_Pa>>8) & 0x00FF
        # SLP_Pa_LSB = SLP_Pa & 0x00FF
        
        # self.i2c.writeto(self.ADDR,bytearray([_BAR_IN_MSB,SLP_Pa_MSB])) #Write MSB offset
        # self.i2c.writeto(self.ADDR,bytearray([_BAR_IN_LSB,SLP_Pa_LSB])) #Write MSB offset
        # print(f'SLP_Pa is {SLP_Pa}')
        # print(f'SLP_mb is {SLP[0]}')

        self.i2c.writeto(self.ADDR,bytearray([_PT_DATA_CFG,0x07])) ##Enable Data Flags
        self.i2c.writeto(self.ADDR,bytearray([_CTRL_REG1,0xB9])) ##Altimeter Mode, 128 OSR, Active with aquisition every 1 second         
        STA = self.i2c.readfrom_mem(self.ADDR,0x00,1) 
        while(not((STA[0]) & (0x08))): ##Check to see if measurement is completed
            time.sleep_ms(500)
            STA = self.i2c.readfrom_mem(self.ADDR,0x00,1)

        
        data = self.i2c.readfrom_mem(0x60,_OUT_P_MSB,3) #Get three bytes starting at _OUT_P_MSB register
        ALT_MSB = data[0]
        ALT_CSB = data[1]
        ALT_LSB = data[2]
        
        station_ALT_meters = (ALT_MSB<<16) | (ALT_CSB<<8) | (ALT_LSB)
        station_ALT_meters = station_ALT_meters >> 4
        station_ALT_meters = station_ALT_meters/16
        
        
        return station_ALT_meters
        #return(SLP_mB,SLP_inHG,SLP_PSI)
        
        
 



if __name__ == "__main__":
    SDA = 8
    SCL = 9
    ID = 0
    ADDR = 0x60
    i2c = I2C(ID, scl = Pin(SCL), sda = Pin(SDA), freq=100000)
    altimeter = MPL3115A2_Altimeter(i2c, ADDR)
    #altimeter.ConnectAndVerify()
    for i in range(10):
        pressure = altimeter.GetSLP()
        altitude = altimeter.GetAltitude()
        #print(pressure[1])
        print(f'Pressure is: {pressure[1]:.2f} inHg and Altitude is: {altitude:.0f} meters')
        
    
    

    