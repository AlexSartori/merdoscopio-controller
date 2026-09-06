import sys

from PyQt6.QtWidgets import QApplication, QFrame, QLabel, QMessageBox, QPlainTextEdit, QWidget, QMainWindow, QPushButton, QHBoxLayout, \
     QVBoxLayout, QGridLayout, QComboBox
from PyQt6.QtCore import Qt, QSize, pyqtSignal as Signal

from merdoscopio.motion_controller import MotionController


CSS_TITLE = '''
    font-size: 18px;
'''

class QHLine(QFrame):
    def __init__(self):
        super(QHLine, self).__init__()
        self.setFrameShape(QFrame.Shape.HLine)
        self.setFrameShadow(QFrame.Shadow.Sunken)


class LogPanel(QWidget):
    def __init__(self):
        super().__init__()

        self.w_title = QLabel("Logs")
        self.w_title.setStyleSheet(CSS_TITLE)

        self.w_txt = QPlainTextEdit("Logs will appear here.")
        self.w_txt.setReadOnly(True)
        self.w_txt.setStyleSheet('''
            background-color: #222;
            color: #eee;
            font-family: mono;
        ''')

        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        layout.addWidget(self.w_title)
        layout.addWidget(self.w_txt)
        self.setLayout(layout)
    
    def addLine(self, line):
        self.w_txt.appendPlainText(line)


class VideoFeed(QWidget):
    def __init__(self):
        super().__init__()

        self.w_title = QLabel("Video feed")
        self.w_title.setStyleSheet(CSS_TITLE)
        
        self.w_video = QWidget()
        self.w_video.setMinimumSize(QSize(400, 400))
        self.w_video.setMaximumSize(QSize(800, 800))
        self.w_video.setStyleSheet("background-color: #bce")

        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        layout.addWidget(self.w_title)
        layout.addWidget(self.w_video)
        self.setLayout(layout)


class MotionControls(QWidget):
    serialDeviceSelected = Signal(str)
    motionRequested = Signal(str, float)
    homingRequested = Signal(str)

    def __init__(self):
        super().__init__()

        self.w_title = QLabel("Motion controls")
        self.w_title.setStyleSheet(CSS_TITLE)

        self.w_lbl_ep = QLabel("Serial endpoint")

        self.w_if_choice = QComboBox()
        self.w_if_choice.currentTextChanged.connect(self.serialDeviceSelected.emit)

        self.w_lbl_loc = QLabel("Axes locations")
        self.w_lbl_x = QLabel("X: ??.??")
        self.w_lbl_y = QLabel("Y: ??.??")
        self.w_lbl_z = QLabel("Z: ??.??")

        self.w_lbl_h = QLabel("Home axes")
        self.w_xh = QPushButton('X')
        self.w_xh.clicked.connect(lambda: self.homingRequested.emit('X'))
        self.w_yh = QPushButton('Y')
        self.w_yh.clicked.connect(lambda: self.homingRequested.emit('Y'))
        self.w_zh = QPushButton('Z')
        self.w_zh.clicked.connect(lambda: self.homingRequested.emit('Z'))

        self.w_lbl_ctr = QLabel("XY control")
        self.w_xn = QPushButton('X-')
        self.w_xp = QPushButton('X+')
        self.w_xp.clicked.connect(self.swag)
        self.w_yn = QPushButton('Y-')
        self.w_yp = QPushButton('Y+')
        self.w_lbl_foc = QLabel("Focus")
        self.w_zn = QPushButton('Z-')
        self.w_zp = QPushButton('Z+')

        layout = QGridLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        layout.addWidget(self.w_title, 0, 0, 1, 3)
        layout.addWidget(self.w_lbl_ep, 1, 0, 1, 3)
        layout.addWidget(self.w_if_choice, 2, 0, 1, 3)
        layout.addWidget(QHLine(), 3, 0, 1, 3)
        layout.addWidget(self.w_lbl_loc, 4, 0, 1, 3)
        layout.addWidget(self.w_lbl_x, 5, 0)
        layout.addWidget(self.w_lbl_y, 5, 1)
        layout.addWidget(self.w_lbl_z, 5, 2)
        layout.addWidget(QHLine(), 6, 0, 1, 3)

        # XYZ homing
        row0 = 7
        layout.addWidget(self.w_lbl_h, row0, 0, 1, 3)
        layout.addWidget(self.w_xh, row0+1, 0)
        layout.addWidget(self.w_yh, row0+1, 1)
        layout.addWidget(self.w_zh, row0+1, 2)
        layout.addWidget(QHLine(), row0+2, 0, 1, 3)

        # XYZ control
        row0 = 11
        layout.addWidget(self.w_lbl_ctr, row0, 0, 1, 3)
        layout.addWidget(self.w_xn, row0+2, 0)
        layout.addWidget(self.w_xp, row0+2, 2)
        layout.addWidget(self.w_yn, row0+3, 1)
        layout.addWidget(self.w_yp, row0+1, 1)
        layout.addWidget(QHLine(), row0+4, 0, 1, 3)
        layout.addWidget(self.w_lbl_foc, row0+5, 0, 1, 3)
        layout.addWidget(self.w_zn, row0+6, 0)
        layout.addWidget(self.w_zp, row0+6, 2)

        self.setLayout(layout)

    def setSerialDevices(self, devices):
        self.w_if_choice.addItems(str(d) for d in devices)

    def swag(self):
        self.motionRequested.emit('x', 20.31)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.controller = MotionController(self.log_serial_msg)
        self.initUI()

    def initUI(self):
        self.setWindowTitle("Merdoscopio controller")
        self.setMinimumSize(QSize(800, 600))

        self.w_serial = LogPanel()
        self.w_serial.setMaximumWidth(800)

        self.w_video = VideoFeed()
        self.w_controls = MotionControls()
        self.w_controls.setSerialDevices(self.controller.getSerialPorts())
        self.w_controls.serialDeviceSelected.connect(self.connectToDevice)
        self.w_controls.homingRequested.connect(self.homeAxis)
        self.w_controls.motionRequested.connect(self.controller.move)

        layout = QHBoxLayout()
        layout.addWidget(self.w_serial)
        layout.addWidget(self.w_video)
        layout.addWidget(self.w_controls)

        widget = QWidget()
        widget.setLayout(layout)
        self.setCentralWidget(widget)

    def connectToDevice(self, device):
        try:
            self.controller.connectAndInitialize(device)
        except Exception as ex:
            msg = f"Could not establish a connection with {device} or initialize it. {ex}"
            QMessageBox.critical(self, "Connection error", msg, QMessageBox.StandardButton.Ok)

    def homeAxis(self, axis):
        try:
            self.controller.homeAxis(axis)
        except Exception as ex:
            QMessageBox.critical(self, "Connection error", f"Could not home axis {axis}. {ex}", QMessageBox.StandardButton.Ok)

    def log_serial_msg(self, msg):
        self.w_serial.addLine(msg)


def launch_gui():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    app.exec()
