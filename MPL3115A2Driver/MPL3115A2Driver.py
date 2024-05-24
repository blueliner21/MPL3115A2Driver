from machine import Pin, I2C
import time

who_am_i = 0x0C
device_id = [0xC4]
CTRL_REG1 = 0x26
OUT_T_MSB = 0x04
OUT_T_LSB = 0x05

class MPL3115A2_Altimeter:

   

    def __init__(self, i2c: I2C, ADDR: int):
        self.i2c = i2c
        self.ADDR = ADDR
    
    def ConnectAndVerify(self): #ToDo: Connect and verify should be in a try loop
        device_id_byte_array = bytearray(device_id)
        if  (self.i2c.readfrom_mem(self.ADDR,who_am_i,1) == device_id_byte_array):
            print("Comms verified. Chip model number confirmed")
        else:
            print("No Comms or Bad Chip") #ToDo: This should raise an exception 
        
    
    def TestDeviceAltimeter(self):
        i2c.writeto(self.ADDR,bytearray([0x26,0xB8]))
        i2c.writeto(self.ADDR,bytearray([0x13,0x07]))
        i2c.writeto(self.ADDR,bytearray([0x26,0xB9]))
        time.sleep_ms(800)
        STA = i2c.readfrom_mem(self.ADDR,0x00,1)
        print(f"Outside Loop STA is {STA}")
        while(not((STA[0]) & (0x08))):
            time.sleep_ms(500)
            STA = i2c.readfrom_mem(self.ADDR,0x00,1)
            print(STA)
        data = i2c.readfrom(self.ADDR,5)
        MSB = data[3]
        LSB = data[4]
        temp = (MSB<<8) | (LSB)
        temp = temp>>4
        temp = temp/16.0
        print(temp)
      
        
        #print(TempMSB)
        #print(TempLSB)



if __name__ == "__main__":
    SDA = 8
    SCL = 9
    ID = 0
    ADDR = 0x60
    i2c = I2C(ID, scl = Pin(SCL), sda = Pin(SDA), freq=100000)
    altimeter = MPL3115A2_Altimeter(i2c, ADDR)
    altimeter.ConnectAndVerify()
    altimeter.TestDeviceAltimeter()
    
    