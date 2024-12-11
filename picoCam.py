from utime import sleep_ms
import utime
import time
import math

import uos
import ujson

from machine import Pin, SPI, reset

'''
Start this alongside the camera module to save photos in a folder with a filename i.e. image-<counter>.jpg
* appends '_' after a word, the next number and the file format
'''
class FileManager:
    def __init__(self, file_manager_name='filemanager.log'):
        
        self.FILE_MANAGER_LOG_NAME = file_manager_name
        self.last_request_filename = None
        self.suffix = None
        count = 0
        file_dict = {}
        # Ensure file is present
        if self.FILE_MANAGER_LOG_NAME not in uos.listdir():
            with open(self.FILE_MANAGER_LOG_NAME, 'w') as f:
                f.write(ujson.dumps(file_dict))
            
        # Check if the filename already exists in the storage
        with open(self.FILE_MANAGER_LOG_NAME, 'r') as f:
            self.file_dict = ujson.loads(f.read())


    def new_jpg_fn(self, requested_filename=None):
        return (self.new_filename(requested_filename) + '.jpg')
    
#     def new_fn_custom(self, suffix, requested_filename=None, suffix):
#         return (self.new_filename(requested_filename) + suffix)
        
    def new_filename(self, requested_filename):
        count = 0
        self.last_request_filename = requested_filename
        
        if requested_filename == None and self.last_request_filename == None:
            raise Exception('Please enter a filename for the first use of the function')
        
        if requested_filename in self.file_dict:
            count = self.file_dict[requested_filename] + 1
        self.file_dict[requested_filename] = count
        
        self.save_manager_file()
        new_filename = f"{requested_filename}_{count}" if count > 0 else f"{requested_filename}"
        
        return new_filename
    
    def save_manager_file(self):
        # Save the updated list back to the storage
        with open(self.FILE_MANAGER_LOG_NAME, 'w') as f:
            f.write(ujson.dumps(self.file_dict))



class Camera:
    # Required imports
    
    ### Register definitions


    ## For camera Reset
    CAM_REG_SENSOR_RESET = 0x07
    CAM_SENSOR_RESET_ENABLE = 0x40
    
    ## For get_sensor_config
    CAM_REG_SENSOR_ID = 0x40
    
    SENSOR_5MP_1 = 0x81
    SENSOR_3MP_1 = 0x82
    SENSOR_5MP_2 = 0x83
    SENSOR_3MP_2 = 0x84
    
    ## Camera effect control
    
    # Set Colour Effect
    CAM_REG_COLOR_EFFECT_CONTROL = 0x27
    
    SPECIAL_NORMAL = 0x00
    SPECIAL_COOL = 1
    SPECIAL_WARM = 2
    SPECIAL_BW = 0x04
    SPECIAL_YELLOWING = 4
    SPECIAL_REVERSE = 5
    SPECIAL_GREENISH = 6
    SPECIAL_LIGHT_YELLOW = 9 # 3MP Only


    # Set Brightness
    CAM_REG_BRIGHTNESS_CONTROL = 0X22

    BRIGHTNESS_MINUS_4 = 8
    BRIGHTNESS_MINUS_3 = 6
    BRIGHTNESS_MINUS_2 = 4
    BRIGHTNESS_MINUS_1 = 2
    BRIGHTNESS_DEFAULT = 0
    BRIGHTNESS_PLUS_1 = 1
    BRIGHTNESS_PLUS_2 = 3
    BRIGHTNESS_PLUS_3 = 5
    BRIGHTNESS_PLUS_4 = 7


    # Set Contrast
    CAM_REG_CONTRAST_CONTROL = 0X23

    CONTRAST_MINUS_3 = 6
    CONTRAST_MINUS_2 = 4
    CONTRAST_MINUS_1 = 2
    CONTRAST_DEFAULT = 0
    CONTRAST_PLUS_1 = 1
    CONTRAST_PLUS_2 = 3
    CONTRAST_PLUS_3 = 5


    # Set Saturation
    CAM_REG_SATURATION_CONTROL = 0X24

    SATURATION_MINUS_3 = 6
    SATURATION_MINUS_2 = 4
    SATURATION_MINUS_1 = 2
    SATURATION_DEFAULT = 0
    SATURATION_PLUS_1 = 1
    SATURATION_PLUS_2 = 3
    SATURATION_PLUS_3 = 5


    # Set Exposure Value
    CAM_REG_EXPOSURE_CONTROL = 0X25

    EXPOSURE_MINUS_3 = 6
    EXPOSURE_MINUS_2 = 4
    EXPOSURE_MINUS_1 = 2
    EXPOSURE_DEFAULT = 0
    EXPOSURE_PLUS_1 = 1
    EXPOSURE_PLUS_2 = 3
    EXPOSURE_PLUS_3 = 5
    
    
    # Set Whitebalance
    CAM_REG_WB_MODE_CONTROL = 0X26
    
    WB_MODE_AUTO = 0
    WB_MODE_SUNNY = 1
    WB_MODE_OFFICE = 2
    WB_MODE_CLOUDY = 3
    WB_MODE_HOME = 4

    # Set Sharpness
    CAM_REG_SHARPNESS_CONTROL = 0X28 #3MP only
    
    SHARPNESS_NORMAL = 0
    SHARPNESS_1 = 1
    SHARPNESS_2 = 2
    SHARPNESS_3 = 3
    SHARPNESS_4 = 4
    SHARPNESS_5 = 5
    SHARPNESS_6 = 6
    SHARPNESS_7 = 7
    SHARPNESS_8 = 8
    
    # Set Autofocus
    CAM_REG_AUTO_FOCUS_CONTROL = 0X29 #5MP only

    # Set Image quality
    CAM_REG_IMAGE_QUALITY = 0x2A
    
    IMAGE_QUALITY_HIGH = 0
    IMAGE_QUALITY_MEDI = 1
    IMAGE_QUALITY_LOW = 2
    
    # Manual gain, and exposure are explored in the datasheet - https://www.arducam.com/downloads/datasheet/Arducam_MEGA_SPI_Camera_Application_Note.pdf

    # Device addressing
    CAM_REG_DEBUG_DEVICE_ADDRESS = 0x0A
    deviceAddress = 0x78
    
    # For Waiting
    CAM_REG_SENSOR_STATE = 0x44
    CAM_REG_SENSOR_STATE_IDLE = 0x01
    
    # Setup for capturing photos
    CAM_REG_FORMAT = 0x20
    
    CAM_IMAGE_PIX_FMT_JPG = 0x01
    CAM_IMAGE_PIX_FMT_RGB565 = 0x02
    CAM_IMAGE_PIX_FMT_YUV = 0x03
    
    # Resolution settings
    CAM_REG_CAPTURE_RESOLUTION = 0x21

    # Some resolutions are not available - refer to datasheet https://www.arducam.com/downloads/datasheet/Arducam_MEGA_SPI_Camera_Application_Note.pdf
#     RESOLUTION_160X120 = 0X00
    RESOLUTION_320X240 = 0X01
    RESOLUTION_640X480 = 0X02
#     RESOLUTION_800X600 = 0X03
    RESOLUTION_1280X720 = 0X04
#     RESOLUTION_1280X960 = 0X05
    RESOLUTION_1600X1200 = 0X06
    RESOLUTION_1920X1080 = 0X07
    RESOLUTION_2048X1536 = 0X08 # 3MP only
    RESOLUTION_2592X1944 = 0X09 # 5MP only
    RESOLUTION_96X96 = 0X0a
    RESOLUTION_128X128 = 0X0b
    RESOLUTION_320X320 = 0X0c
    
    valid_3mp_resolutions = {
        '320x240': RESOLUTION_320X240, 
        '640x480': RESOLUTION_640X480, 
        '1280x720': RESOLUTION_1280X720, 
        '1600x1200': RESOLUTION_1600X1200,
        '1920x1080': RESOLUTION_1920X1080,
        '2048x1536': RESOLUTION_2048X1536,
        '96X96': RESOLUTION_96X96,
        '128X128': RESOLUTION_128X128,
        '320X320': RESOLUTION_320X320
    }

    valid_5mp_resolutions = {
        '320x240': RESOLUTION_320X240, 
        '640x480': RESOLUTION_640X480, 
        '1280x720': RESOLUTION_1280X720, 
        '1600x1200': RESOLUTION_1600X1200,
        '1920x1080': RESOLUTION_1920X1080,
        '2592x1944': RESOLUTION_2592X1944,
        '96X96': RESOLUTION_96X96,
        '128X128': RESOLUTION_128X128,
        '320X320': RESOLUTION_320X320
    }

    # FIFO and State setting registers
    ARDUCHIP_FIFO = 0x04
    FIFO_CLEAR_ID_MASK = 0x01
    FIFO_START_MASK = 0x02
    
    ARDUCHIP_TRIG = 0x44
    CAP_DONE_MASK = 0x04
    
    FIFO_SIZE1 = 0x45
    FIFO_SIZE2 = 0x46
    FIFO_SIZE3 = 0x47
    
    SINGLE_FIFO_READ = 0x3D
    BURST_FIFO_READ = 0X3C
    
    # Size of image_buffer (Burst reading)
    BUFFER_MAX_LENGTH = 1024
    
    # For 5MP startup routine
    WHITE_BALANCE_WAIT_TIME_MS = 500


# User callable functions
## Main functions
## Setting functions
# Internal functions
## High level internal functions
## Low level

##################### Callable FUNCTIONS #####################

########### CORE PHOTO FUNCTIONS ###########
    def __init__(self, spi_bus, cs, skip_sleep=False, debug_information=False):
        self.cs = cs
        self.spi_bus = spi_bus

        self._write_reg(self.CAM_REG_SENSOR_RESET, self.CAM_SENSOR_RESET_ENABLE) # Reset camera
        self._wait_idle()
        self._get_sensor_config() # Get camera sensor information
        self._wait_idle()
        self._write_reg(self.CAM_REG_DEBUG_DEVICE_ADDRESS, self.deviceAddress)
        self._wait_idle()

        self.run_start_up_config = True

        # Set default format and resolution
        self.current_pixel_format = self.CAM_IMAGE_PIX_FMT_JPG
        self.old_pixel_format = self.current_pixel_format
        
        self.current_resolution_setting = self.RESOLUTION_640X480 # ArduCam driver defines this as mode
        self.old_resolution = self.current_resolution_setting
        
        
        self.set_filter(self.SPECIAL_NORMAL)
        
        self.received_length = 0
        self.total_length = 0
        
        # Burst setup
        self.first_burst_run = False
        self.image_buffer = bytearray(self.BUFFER_MAX_LENGTH)
        self.valid_image_buffer = 0
        
        self.camera_idx = 'NOT DETECTED'
        
        
        # Tracks the AWB warmup time
        self.start_time = utime.ticks_ms()
        if debug_information:
            print('Camera version =', self.camera_idx)
        if self.camera_idx == '3MP':
            self.startup_routine_3MP()
        
        if self.camera_idx == '5MP' and skip_sleep == False:
            utime.sleep_ms(self.WHITE_BALANCE_WAIT_TIME_MS)


    def startup_routine_3MP(self):
        # Leave the shutter open for some time seconds (i.e. take a few photos without saving)
        print('Running 3MP startup routine')
        self.capture_jpg()
        self.saveJPG('dummy_image.jpg')
        uos.remove('dummy_image.jpg')
        print('complete')

    '''
    Issue warning if the filepath doesnt end in .jpg (Blank) and append
    Issue error if the filetype is NOT .jpg
    '''
    def capture_jpg(self):

        if (utime.ticks_diff(utime.ticks_ms(), self.start_time) <= self.WHITE_BALANCE_WAIT_TIME_MS) and self.camera_idx == '5MP':
            print('Please add a ', self.WHITE_BALANCE_WAIT_TIME_MS, 'ms delay to allow for white balance to run')
        else:
#             print('Starting capture JPG')
            # JPG, bmp ect
            # TODO: PROPERTIES TO CONFIGURE THE PIXEL FORMAT
            if (self.old_pixel_format != self.current_pixel_format) or self.run_start_up_config:
                self.old_pixel_format = self.current_pixel_format
                self._write_reg(self.CAM_REG_FORMAT, self.current_pixel_format) # Set to capture a jpg
                self._wait_idle()
#             print('old',self.old_resolution,'new',self.current_resolution_setting)
                # TODO: PROPERTIES TO CONFIGURE THE RESOLUTION
            if (self.old_resolution != self.current_resolution_setting) or self.run_start_up_config:
                self.old_resolution = self.current_resolution_setting
                self._write_reg(self.CAM_REG_CAPTURE_RESOLUTION, self.current_resolution_setting)
#                 print('setting res', self.current_resolution_setting)
                self._wait_idle()
            self.run_start_up_config = False
            
            # Start capturing the photo
            self._set_capture()
#             print('capture jpg complete')
        

    # TODO: After reading the camera data clear the FIFO and reset the camera (so that the first time read can be used)
    def saveJPG(self,filename):
        headflag = 0
        print('Saving image, please dont remove power')
#         print('rec len:', self.received_length)
        
        image_data = 0x00
        image_data_next = 0x00
        
        image_data_int = 0x00
        image_data_next_int = 0x00
        
        print(self.received_length)
        
        while(self.received_length):
            
            image_data = image_data_next
            image_data_int = image_data_next_int
            
            image_data_next = self._read_byte()
            image_data_next_int = int.from_bytes(image_data_next, 1) # TODO: CHANGE TO READ n BYTES
            if headflag == 1:
                jpg_to_write.write(image_data_next)
            
            if (image_data_int == 0xff) and (image_data_next_int == 0xd8):
                # TODO: Save file to filename
#                 print('start of file')
                headflag = 1
                jpg_to_write = open(filename,'ab')
                jpg_to_write.write(image_data)
                jpg_to_write.write(image_data_next)
                
            if (image_data_int == 0xff) and (image_data_next_int == 0xd9):
#                 print('TODO: Save and close file?')
                headflag = 0
                jpg_to_write.write(image_data_next)
                jpg_to_write.close()
                
    def getImageData(self, esp32CS, esp32SPI):
        headflag = 0
        print('Saving image, please dont remove power')
#         print('rec len:', self.received_length)
        
        image_data = 0x00
        image_data_next = 0x00
        
        image_data_int = 0x00
        image_data_next_int = 0x00
        
        print(self.received_length)
        
        data = []
        i = 0
        
        while(self.received_length):
            print(i)
            i+=1
            image_data = image_data_next
            image_data_int = image_data_next_int
            
            image_data_next = self._read_byte()
            print(f'data next {image_data_next}')
            image_data_next_int = int.from_bytes(image_data_next, 1) # TODO: CHANGE TO READ n BYTES
            if headflag == 1:
                data = image_data_next
                print("write 1")
                esp32CS.low()
                esp32SPI.write(image_data_next)
                esp32CS.high()
            
            if (image_data_int == 0xff) and (image_data_next_int == 0xd8):
                headflag = 1
                print("write 2")
                esp32CS.low()
                esp32SPI.write(image_data)
                esp32SPI.write(image_data_next)
                esp32CS.high()
                
            if (image_data_int == 0xff) and (image_data_next_int == 0xd9):
                headflag = 0
                print("write 3")
                esp32CS.low()
                esp32SPI.write(image_data_next)
                esp32CS.high()
            time.sleep(.01)
        return data





    def save_JPG_burst(self):
        headflag = 0
        print('Saving image, please dont remove power')

        image_data = 0x00
        image_data_next = 0x00

        image_data_int = 0x00
        image_data_next_int = 0x00

        print(self.received_length)

        while(self.received_length):
            self._burst_read_FIFO()
            
            start_bytes = self.image_buffer[0]
            end_bytes = self.image_buffer[self.valid_image_buffer-1]
            
        
#     def _read_byte(self):
#         self.cs.off()
#         self.spi_bus.write(bytes([self.SINGLE_FIFO_READ]))
#         data = self.spi_bus.read(1)
#         data = self.spi_bus.read(1)
#         self.cs.on()
#         self.received_length -= 1
#         return data


    def _burst_read_FIFO(self):
        #compute how many bytes to read
        burst_read_length = self.BUFFER_MAX_LENGTH # Default to max length
        if self.received_length < self.BUFFER_MAX_LENGTH:
            burst_read_length = self.received_length
        current_buffer_byte = 0
        
        self.cs.off()
        self.spi_bus.write(bytes([self.BURST_FIFO_READ]))
        
        # Throw away first byte on first read
        if self.first_burst_fifo == True:
            data = self.spi_bus.read(1)
            self.first_burst_fifo = False
            
        total_read = 0
        while total_read < burst_read_length:
            data = self.spi_bus.read(1) # Read from camera
            self.image_buffer[current_buffer_byte] = data[0] # write to buffer
            current_buffer_byte += 1
            total_read += 1

        self.cs.on()
        self.received_length -= burst_read_length
        self.valid_image_buffer = burst_read_length
        
    def _burst_read_FIFO_faster(self):
        #compute how many bytes to read
        burst_read_length = self.BUFFER_MAX_LENGTH # Default to max length
        if self.received_length < self.BUFFER_MAX_LENGTH:
            burst_read_length = self.received_length
        current_buffer_byte = 0
        
        self.cs.off()
        self.spi_bus.write(bytes([self.BURST_FIFO_READ]))
        
        # Throw away first byte on first read
        if self.first_burst_fifo == True:
            data = self.spi_bus.read(1)
            self.first_burst_fifo = False
            
        total_read = 0
        self.image_buffer = self.spi_bus.read(burst_read_length)
        
        if self.received_length < self.BUFFER_MAX_LENGTH:
            self.image_buffer = bytearray(self.image_buffer)
            for i in range(self.received_length, self.BUFFER_MAX_LENGTH):
                self.image_buffer.append(0)

        self.cs.on()
        self.received_length -= burst_read_length
        self.valid_image_buffer = burst_read_length


    @property
    def resolution(self):
        return self.current_resolution_setting
    @resolution.setter
    def resolution(self, new_resolution):
        input_string_lower = new_resolution.lower()        
        if self.camera_idx == '3MP':
            if input_string_lower in self.valid_3mp_resolutions:
                self.current_resolution_setting = self.valid_3mp_resolutions[input_string_lower]
            else:
                raise ValueError("Invalid resolution provided for {}, please select from {}".format(self.camera_idx, list(self.valid_3mp_resolutions.keys())))

        elif self.camera_idx == '5MP':
            if input_string_lower in self.valid_5mp_resolutions:
                self.current_resolution_setting = self.valid_5mp_resolutions[input_string_lower]
            else:
                raise ValueError("Invalid resolution provided for {}, please select from {}".format(self.camera_idx, list(self.valid_5mp_resolutions.keys())))
    

    def set_pixel_format(self, new_pixel_format):
        self.current_pixel_format = new_pixel_format

########### ACCSESSORY FUNCTIONS ###########

    # TODO: Complete for other camera settings
    # Make these setters - https://github.com/CoreElectronics/CE-PiicoDev-Accelerometer-LIS3DH-MicroPython-Module/blob/abcb4337020434af010f2325b061e694b808316d/PiicoDev_LIS3DH.py#L118C1-L118C1
    
#     # Set Brightness
#     CAM_REG_BRIGHTNESS_CONTROL = 0X22
# 
#     BRIGHTNESS_MINUS_4 = 8
#     BRIGHTNESS_MINUS_3 = 6
#     BRIGHTNESS_MINUS_2 = 4
#     BRIGHTNESS_MINUS_1 = 2
#     BRIGHTNESS_DEFAULT = 0
#     BRIGHTNESS_PLUS_1 = 1
#     BRIGHTNESS_PLUS_2 = 3
#     BRIGHTNESS_PLUS_3 = 5
#     BRIGHTNESS_PLUS_4 = 7


    def set_brightness_level(self, brightness):
        self._write_reg(self.CAM_REG_BRIGHTNESS_CONTROL, brightness)
        self._wait_idle()

    def set_filter(self, effect):
        self._write_reg(self.CAM_REG_COLOR_EFFECT_CONTROL, effect)
        self._wait_idle()

#     # Set Saturation
#     CAM_REG_SATURATION_CONTROL = 0X24
# 
#     SATURATION_MINUS_3 = 6
#     SATURATION_MINUS_2 = 4
#     SATURATION_MINUS_1 = 2
#     SATURATION_DEFAULT = 0
#     SATURATION_PLUS_1 = 1
#     SATURATION_PLUS_2 = 3
#     SATURATION_PLUS_3 = 5

    def set_saturation_control(self, saturation_value):
        self._write_reg(self.CAM_REG_SATURATION_CONTROL, saturation_value)
        self._wait_idle()

#     # Set Exposure Value
#     CAM_REG_EXPOSURE_CONTROL = 0X25
# 
#     EXPOSURE_MINUS_3 = 6
#     EXPOSURE_MINUS_2 = 4
#     EXPOSURE_MINUS_1 = 2
#     EXPOSURE_DEFAULT = 0
#     EXPOSURE_PLUS_1 = 1
#     EXPOSURE_PLUS_2 = 3
#     EXPOSURE_PLUS_3 = 5


#     # Set Contrast
#     CAM_REG_CONTRAST_CONTROL = 0X23
# 
#     CONTRAST_MINUS_3 = 6
#     CONTRAST_MINUS_2 = 4
#     CONTRAST_MINUS_1 = 2
#     CONTRAST_DEFAULT = 0
#     CONTRAST_PLUS_1 = 1
#     CONTRAST_PLUS_2 = 3
#     CONTRAST_PLUS_3 = 5

    def set_contrast(self, contrast):
        self._write_reg(self.CAM_REG_CONTRAST_CONTROL, contrast)
        self._wait_idle()


    def set_white_balance(self, environment):
        register_value = self.WB_MODE_AUTO

        if environment == 'sunny':
            register_value = self.WB_MODE_SUNNY
        elif environment == 'office':
            register_value = self.WB_MODE_OFFICE
        elif environment == 'cloudy':
            register_value = self.WB_MODE_CLOUDY
        elif environment == 'home':
            register_value = self.WB_MODE_HOME
        elif self.camera_idx == '3MP':
            print('TODO UPDATE: For best results set a White Balance setting')

        self.white_balance_mode = register_value
        self._write_reg(self.CAM_REG_WB_MODE_CONTROL, register_value)
        self._wait_idle()

##################### INTERNAL FUNCTIONS - HIGH LEVEL #####################

########### CORE PHOTO FUNCTIONS ###########
    def _clear_fifo_flag(self):
        self._write_reg(self.ARDUCHIP_FIFO, self.FIFO_CLEAR_ID_MASK)

    def _start_capture(self):
        self._write_reg(self.ARDUCHIP_FIFO, self.FIFO_START_MASK)

    def _set_capture(self):
#         print('a1')
        self._clear_fifo_flag()
        self._wait_idle()
        self._start_capture()
#         print('a2')
        while (int(self._get_bit(self.ARDUCHIP_TRIG, self.CAP_DONE_MASK)) == 0):
#             print(self._get_bit(self.ARDUCHIP_TRIG, self.CAP_DONE_MASK))
            sleep_ms(1)
#         print('a3')
        self.received_length = self._read_fifo_length()
        self.total_length = self.received_length
        self.burst_first_flag = False
#         print('a4')
    
    def _read_fifo_length(self): # TODO: CONFIRM AND SWAP TO A 3 BYTE READ
        len1 = int.from_bytes(self._read_reg(self.FIFO_SIZE1),1)
        len2 = int.from_bytes(self._read_reg(self.FIFO_SIZE2),1)
        len3 = int.from_bytes(self._read_reg(self.FIFO_SIZE3),1)
        return ((len3 << 16) | (len2 << 8) | len1) & 0xffffff

    def _get_sensor_config(self):
        camera_id = self._read_reg(self.CAM_REG_SENSOR_ID);
        self._wait_idle()
        if (int.from_bytes(camera_id, 1) == self.SENSOR_3MP_1) or (int.from_bytes(camera_id, 1) == self.SENSOR_3MP_2):
            self.camera_idx = '3MP'
        if (int.from_bytes(camera_id, 1) == self.SENSOR_5MP_1) or (int.from_bytes(camera_id, 1) == self.SENSOR_5MP_2):
            self.camera_idx = '5MP'


##################### INTERNAL FUNCTIONS - LOW LEVEL #####################

    def _read_buffer(self):
        print('COMPLETE')

    def _bus_write(self, addr, val):
        self.cs.off()
        self.spi_bus.write(bytes([addr]))
        self.spi_bus.write(bytes([val])) # FixMe only works with single bytes
        self.cs.on()
        sleep_ms(1) # From the Arducam Library
        return 1
    
    def _bus_read(self, addr):
        self.cs.off()
        self.spi_bus.write(bytes([addr]))
        data = self.spi_bus.read(1) # Only read second set of data
        data = self.spi_bus.read(1)
        self.cs.on()
        return data

    def _write_reg(self, addr, val):
        self._bus_write(addr | 0x80, val)

    def _read_reg(self, addr):
        data = self._bus_read(addr & 0x7F)
        return data # TODO: Check that this should return raw bytes or int (int.from_bytes(data, 1))

    def _read_byte(self):
        self.cs.off()
        self.spi_bus.write(bytes([self.SINGLE_FIFO_READ]))
        data = self.spi_bus.read(1)
        data = self.spi_bus.read(1)
        self.cs.on()
        self.received_length -= 1
        return data
    
    def _wait_idle(self):
        data = self._read_reg(self.CAM_REG_SENSOR_STATE)
        while ((int.from_bytes(data, 1) & 0x03) == self.CAM_REG_SENSOR_STATE_IDLE):
            data = self._read_reg(self.CAM_REG_SENSOR_STATE)
            sleep_ms(2)

    def _get_bit(self, addr, bit):
        data = self._read_reg(addr);
        return int.from_bytes(data, 1) & bit;

# SPIMODE0 is 0-Polarity and 0-Phase
# SPIMODE1 is 0-Polarity and 1-Phase
# SPIMODE2 is 1-Polarity and 0-Phase
# SPIMODE3 is 1-Polarity and 1-Phase
esp32SPI = SPI(1, baudrate=8000000, polarity=0, phase=1, bits=8, sck=machine.Pin(10), mosi=machine.Pin(11), miso=machine.Pin(12))
esp32CS = Pin(13, Pin.OUT)
esp32CS.high()

camSPI = SPI(0,sck=Pin(18), miso=Pin(16), mosi=Pin(19), baudrate=8000000)
camCS = Pin(17, Pin.OUT)

# button = Pin(15, Pin.IN,Pin.PULL_UP)
onboard_LED = Pin(25, Pin.OUT)

cam = Camera(camSPI, camCS)
# 320x240 1280x720
cam.resolution = '1280x720'
# cam.resolution('1280x720')
cam.set_filter(cam.SPECIAL_REVERSE)
cam.set_brightness_level(cam.BRIGHTNESS_PLUS_4)
cam.set_contrast(cam.CONTRAST_MINUS_3)


# onboard_LED.on()
esp32CS.on()
while True:
    start_capture_time = time.ticks_ms()
    cam.capture_jpg()
    end_capture_time = time.ticks_ms()
    i = 0

    totalMessages = math.ceil(cam.received_length / cam.BUFFER_MAX_LENGTH)
    readBuf1 = bytearray(cam.BUFFER_MAX_LENGTH)
    readBuf2 = bytearray(cam.BUFFER_MAX_LENGTH)
    metadataMessage = bytearray(cam.received_length.to_bytes(4) + totalMessages.to_bytes(4) + bytearray(cam.BUFFER_MAX_LENGTH - 8))
    # Sending hardcoded data so the slave knows that this is metadata 
    metadataMessage[-1] = 22
    metadataMessage[-2] = 222
    readyToBurstSend = False
    start_handshake_time = time.ticks_ms()
    esp32CS.off()
    while readyToBurstSend is False:
        # We need a write read to ensure a full duplex transaction is made
        esp32SPI.write_readinto(metadataMessage, readBuf1)
        # Checking for a valid slave response, expect the slave to send back a nothing but 222
        if readBuf1[0] == 222:
            readyToBurstSend = True
    esp32CS.on()
    end_handshake_time = time.ticks_ms()
    
    start_transaction_time = time.ticks_ms()
    cam.first_burst_fifo = True
    esp32CS.off()
    cam_total_read_time = 0
    slave_total_write_time = 0
    while(cam.received_length):
#         cam._burst_read_FIFO()
        start_cam_read = time.ticks_ms()
        cam._burst_read_FIFO_faster()
        end_cam_read = time.ticks_ms()
        start_slave_write = time.ticks_ms()
        esp32SPI.write(cam.image_buffer)
        end_slave_write = time.ticks_ms()
        cam_total_read_time += end_cam_read - start_cam_read
        slave_total_write_time += end_slave_write - start_slave_write
        i += 1
    esp32CS.on()
    print(f"sent messages: {i}")
    print(f"cam transaction duration: {cam_total_read_time}")
    print(f"slave transaction duration: {slave_total_write_time}")
    print(f"handshake duration: {end_handshake_time - start_handshake_time}")
    print(f"capture duration: {end_capture_time - start_capture_time}")


    




