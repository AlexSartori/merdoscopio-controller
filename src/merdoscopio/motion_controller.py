import serial
from serial.tools import list_ports

SERIAL_TOUT_S = 5
SERIAL_BAUD = 115200

INIT_SEQUENCE = [
    "G21",   # Set units to mm
    "G91",   # Set relative mode
    "G0 F50" # Set a sensible speed
]

class MotionController:
    def __init__(self, serial_log_cb):
        self.serial_log_cb = serial_log_cb
        self.modem = None
        self.is_connected = False


    def getSerialPorts(self):
        return  [p.device for p in list_ports.comports()]


    def sendAndConfirm(self, cmd: str):
        if self.modem is None or not self.is_connected:
            raise ConnectionError("No endpoint is connected")

        self.modem.write((cmd+'\n').encode('utf-8'))
        reply = self.modem.read_until(b'ok').decode().strip().lower()
        print(cmd, reply)

        if reply != 'ok':
            # raise Exception(f"Unexpected reply from endpoint: 'ok' != '{reply}'")
            print(f"Unexpected reply from endpoint: 'ok' != '{reply}'")
        self.serial_log_cb(f"Sent off: [{cmd}] ({reply})")


    def connectAndInitialize(self, device: str) -> bool:
        self.modem = serial.Serial(device, SERIAL_BAUD, timeout=SERIAL_TOUT_S)
        self.is_connected = True

        try:
            for cmd in INIT_SEQUENCE:
                self.sendAndConfirm(cmd)
        except TimeoutError as ex:
            self.model = None
            self.is_connected = False
            self.serial_log_cb(f"Timed out waiting for device {device}.")
            raise ex


    def move(self, axis, amount, rate):
        self.serial_log_cb(f"Moving axis {axis} by {amount}mm at rate F{rate}")
        self.sendAndConfirm(f"G0 {axis}{amount} F{rate}")


    def homeAxis(self, axis):
        axis = str(axis).upper()
        if axis not in 'XYZ':
            raise ValueError(f"Invalid axis to home: {axis}. Must be X, Y, or Z.")
        self.serial_log_cb(f"Homing {axis}...")
        self.sendAndConfirm(f"G20 {axis}")