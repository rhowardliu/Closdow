import serial
import logging


logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)


address = '/dev/ttyACM0'

try:
    ser = serial.Serial(address, 9600)
except FileNotFoundError:
    set_serial_address(add='ttyACM1')


def set_serial_address(add = 'ttyACM0'):
    global address
    address = '/dev/' + add


def open():
    ser.write(b'o')


def close():
    ser.write(b'c')


def set_child_lock():
    ser.write(b'l')

def disable_child_lock():
    ser.write(b'u')

def enable_sensor():
    ser.write(b'e')

def disable_sensor():
    ser.write(b'd')

def fetch_window_state_change():
    receivedChar = ser.readline()
    logger.info("received from arduino: " + receivedChar)
    return receivedChar
