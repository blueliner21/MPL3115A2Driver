from machine import Pin, I2C

who_am_i = 0x0C
device_id = [0xC4]

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
        
    
    def GetStationPressure(self):
        pass



if __name__ == "__main__":
    SDA = 8
    SCL = 9
    ID = 0
    ADDR = 0x60
    i2c = I2C(ID, scl = Pin(SCL), sda = Pin(SDA), freq=100000)
    altimeter = MPL3115A2_Altimeter(i2c, ADDR)
    altimeter.ConnectAndVerify()
   
    