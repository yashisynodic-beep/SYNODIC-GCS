from PyQt5 import QtCore, QtGui, QtWidgets
from ics_rc import *
#from PyQt5.QtGui import QMovie
from PyQt5.QtWidgets import QWidget
#from PyQt5.QtGui import QFontDatabase
from stl_view import STLView

class DbWindow(QtWidgets.QWidget):
   
    def __init__(self, serial_manager, stl_view):
        super().__init__()
        self.serial_manager = serial_manager  # ✅ SAME instance
        self.stl_view = stl_view
        self.setupUi(self)
        self.serial_manager.data_received.connect(self.update_data)
        self.serial_manager.data_received.connect(self.update_stl_from_serial)
        self.progressBar_7.setMaximum(100)
        self.progressBar_8.setMaximum(100)
        self.progressBar_9.setMaximum(100)
        self.progressBar_11.setMaximum(100)
        self.progressBar_12.setMaximum(100)


        self.last_update_time = 0
        self.update_interval_ms = 200
        self.last_energy_time = QtCore.QDateTime.currentMSecsSinceEpoch()
        self.total_energy_Wh = 0.0

        # Set your battery capacity here (example: 2200mAh 3S Li-ion)
        self.battery_capacity_Wh = 11.1 * 2.2   # 11.1V × 2.2Ah = 24.42Wh

        self.telemetry_fields = [
            "Rocket_ID",
            "Mission Time",
            "Packet Count",
            "Altitude",
            "Pressure",
            "Load Voltage",
            "Load Current",
            "GPS Latitude",
            "GPS Longitude",
            "Accel X",
            "Accel Y",
            "Accel Z",
            "Gyro X",
            "Gyro Y",
            "Gyro Z", "Mag X", "Mag Y", "Mag Z",
            "Euler X", "Euler Y", "Euler Z",
            "State", 
        ]

        # Core telemetry
        self.field_widgets = {
            # Rocket Info
            "Rocket_ID": self.label_3,
            "Mission Time": self.label_5,
            "Packet Count": self.label_7,

            # Core Telemetry
            "Altitude": self.label_8,
            "Pressure": self.label_10,
            "Load Voltage": self.label_12,
            "Load Current": self.label_14,

            # GPS
            "GPS Latitude": self.label_16,
            "GPS Longitude": self.label_18,

            # Accelerometer
            "Accel X": self.label_33,
            "Accel Y": self.label_35,
            "Accel Z": self.label_37,

            # Gyroscope
            "Gyro X": self.label_39,
            "Gyro Y": self.label_41,
            "Gyro Z": self.label_43,

            # Magnetometer
            "Mag X": self.label_21,
            "Mag Y": self.label_24,
            "Mag Z": self.label_25,

            # Euler Angles
            "Euler X": self.label_27,
            "Euler Y": self.label_29,
            "Euler Z": self.label_31,

            # State
            "State": self.label_44,

            # Battery 
            "Battery": self.progressBar_7,
        }

        
    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.resize(946, 575)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(Form.sizePolicy().hasHeightForWidth())
        Form.setSizePolicy(sizePolicy)
        Form.setStyleSheet(
"QWidget {\n"
"    background: qlineargradient(\n"
"        x1:0, y1:0, x2:1, y2:1,\n"
"        stop:0   #020B1E,\n"
"        stop:0.35 #061A35,\n"
"        stop:0.7 #0A2C5A,\n"
"        stop:1     #0F3E78 \n"
"    );\n"

"}\n"

"QFrame#rootFrame {\n"
"    background: transparent;\n"
"    border: none;\n"
"}\n"
"    border: 1px solid rgba(140,220,255,0.55);\n"
"}\n"

"QFrame#frame_2 {\n"
"    background: qlineargradient(\n"
"        x1:0, y1:0,\n"
"        x2:1, y2:1,\n"
"        stop:0   rgba(0,230,255,0.18),  /* #00E6FF neon cyan */\n"
"        stop:0.35 rgba(28,203,255,0.16), /* #1CCBFF */\n"
"        stop:0.7  rgba(63,169,245,0.14), /* #3FA9F5 */\n"
"        stop:1    rgba(79,195,255,0.12)  /* #4FC3FF */\n"
"    );\n"
"    border-radius: 16px;\n"
"\n"
"    /* Glass edge + glow */\n"
"    border: 1px solid rgba(110,231,255,0.45); /* #6EE7FF */\n"
"}\n"

"QFrame#frame_3, QFrame#frame_4, QFrame#frame_5, QFrame#frame_6,\n"
"QFrame#frame_7, QFrame#frame_8, QFrame#frame_9, QFrame#frame_10,\n"
"QFrame#frame_11, QFrame#frame_12, QFrame#frame_13, QFrame#frame_14,\n"
"QFrame#frame_15, QFrame#frame_16 {\n"
"\n"
"    background: qlineargradient(\n"
"        x1:0, y1:0,\n"
"        x2:0, y2:1,\n"
"        stop:0 rgba(0, 230, 255, 0.15),  /* soft cyan glass */\n"
"        stop:0.6 rgba(79, 195, 255, 0.20) /* HUD panel tint */\n"
"    );\n"
"\n"
"    border-radius: 16px;\n"
"    border: 1px solid rgba(30, 120, 200, 0.35); /* base sci-fi border */\n"
"}\n"

"QLabel {\n"
"    background: rgba(0, 230, 255, 0.08);   /* soft cyan glass */\n"
"    color: #9FEFFF;                      /* primary HUD label */\n"

"    font-size: 13px;\n"
"    font-weight: 500;\n"
"font-size: 14px;\n"
"    padding: 6px 10px;\n"
"    border-radius: 8px;\n"
"    border: 1px solid rgba(0, 160, 255, 0.35);\n"
"}\n"

"QLabel#valueLabel {\n"
"    background: rgba(0, 230, 255, 0.12);\n"
"    color: #00E6FF;\n"

"    font-weight: 600;\n"
"font-size: 16px;\n"
"    letter-spacing: 0.5px;\n"
"    border: 1px solid rgba(0, 230, 255, 0.55);\n"
"}\n"

"QLabel:hover {\n"
"    border: 1px solid rgba(0, 230, 255, 0.65);\n"
"}\n"

"QLineEdit, QComboBox {\n"
"    background: rgba(5, 30, 55, 0.78);\n"
"    color: #E4FAFF;\n"
"    border-radius: 8px;\n"
"    border: 1px solid rgba(90,200,255,0.55);\n"
"    padding: 6px;\n"
"     font-size: 16px;\n"
"}\n"

"QProgressBar {\n"
"    background: rgba(10, 45, 80, 0.75);\n"
"    border-radius: 8px;\n"
"    border: 1px solid rgba(90,180,240,0.45);\n"
"    height: 14px;\n"
"    text-align: center;\n"
"    color: #EAFBFF;\n"
"}\n"

"QProgressBar::chunk {\n"
"    border-radius: 8px;\n"
"    background: qlineargradient(\n"
"        x1:0, y1:0, x2:1, y2:0,\n"
"        stop:0   #00EFFF,\n"
"        stop:0.5 #4FB9FF,\n"
"        stop:1   #B6F7FF\n"
"    );\n"
"}\n"

"QPushButton {\n"
"    background: qlineargradient(\n"
"        x1:0, y1:0, x2:1, y2:1,\n"
"        stop:0 #4FD2FF,\n"
"        stop:1 #1E7AC7\n"
"    );\n"
"    color: #052638;\n"
"    border-radius: 12px;\n"
"    border: 1px solid rgba(160,240,255,0.65);\n"
"    padding: 6px 18px;\n"
"    font-weight: 600;\n"
"}\n"

"QPushButton:hover {\n"
"    background: qlineargradient(\n"
"        x1:0, y1:0, x2:1, y2:1,\n"
"        stop:0 #7BE9FF,\n"
"        stop:1 #3B9CFF\n"
"    );\n"
"}\n"

"QPushButton:pressed {\n"
"    background: rgba(30,110,170,0.95);\n"
"}\n"
)


        
        self.gridLayout = QtWidgets.QGridLayout(Form)
        self.gridLayout.setObjectName("gridLayout")
        self.rootFrame = QtWidgets.QFrame(Form)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.rootFrame.sizePolicy().hasHeightForWidth())
        self.rootFrame.setSizePolicy(sizePolicy)
        self.rootFrame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.rootFrame.setFrameShadow(QtWidgets.QFrame.Raised)
        self.rootFrame.setObjectName("rootFrame")
        self.gridLayout_9 = QtWidgets.QGridLayout(self.rootFrame)
        self.gridLayout_9.setSpacing(12)
        self.gridLayout_9.setObjectName("gridLayout_9")
        self.frame_2 = QtWidgets.QFrame(self.rootFrame)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.frame_2.sizePolicy().hasHeightForWidth())
        self.frame_2.setSizePolicy(sizePolicy)
        self.frame_2.setMinimumSize(QtCore.QSize(0, 300))
        self.frame_2.setMaximumSize(QtCore.QSize(16777215, 16777215))
        self.frame_2.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.frame_2.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame_2.setObjectName("frame_2")
        self.gridLayout_6 = QtWidgets.QGridLayout(self.frame_2)
        self.gridLayout_6.setContentsMargins(12, 6, 4, 4)
        self.gridLayout_6.setSpacing(4)
        self.gridLayout_6.setObjectName("gridLayout_6")
        self.gridLayout_7 = QtWidgets.QGridLayout()
        self.gridLayout_7.setObjectName("gridLayout_7")
        self.gridLayout_5 = QtWidgets.QGridLayout()
        self.gridLayout_5.setObjectName("gridLayout_5")
        self.frame_15 = QtWidgets.QFrame(self.frame_2)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.frame_15.sizePolicy().hasHeightForWidth())
        self.frame_15.setSizePolicy(sizePolicy)
        self.frame_15.setFixedSize(230, 150)
        self.frame_15.setFrameShape(QtWidgets.QFrame.Box)
        self.frame_15.setFrameShadow(QtWidgets.QFrame.Plain)
        self.frame_15.setObjectName("frame_15")
        self.horizontalLayout_4 = QtWidgets.QHBoxLayout(self.frame_15)
        self.horizontalLayout_4.setContentsMargins(4, 4, 4, 4)
        self.horizontalLayout_4.setObjectName("horizontalLayout_4")
        self.gridLayout_4 = QtWidgets.QGridLayout()
        self.gridLayout_4.setContentsMargins(9, 9, 9, 9)
        self.gridLayout_4.setSpacing(9)
        self.gridLayout_4.setObjectName("gridLayout_4")
        self.label_38 = QtWidgets.QLabel(self.frame_15)
        self.label_38.setAlignment(QtCore.Qt.AlignCenter)
        self.label_38.setObjectName("label_38")
        self.gridLayout_4.addWidget(self.label_38, 0, 0, 1, 1)
        self.label_39 = QtWidgets.QLabel(self.frame_15)
        self.label_39.setText("")
        self.label_39.setObjectName("label_39")
        self.gridLayout_4.addWidget(self.label_39, 0, 1, 1, 1)
        self.label_40 = QtWidgets.QLabel(self.frame_15)
        self.label_40.setAlignment(QtCore.Qt.AlignCenter)
        self.label_40.setObjectName("label_40")
        self.gridLayout_4.addWidget(self.label_40, 1, 0, 1, 1)
        self.label_41 = QtWidgets.QLabel(self.frame_15)
        self.label_41.setText("")
        self.label_41.setObjectName("label_41")
        self.gridLayout_4.addWidget(self.label_41, 1, 1, 1, 1)
        self.label_42 = QtWidgets.QLabel(self.frame_15)
        self.label_42.setAlignment(QtCore.Qt.AlignCenter)
        self.label_42.setObjectName("label_42")
        self.gridLayout_4.addWidget(self.label_42, 2, 0, 1, 1)
        self.label_43 = QtWidgets.QLabel(self.frame_15)
        self.label_43.setText("")
        self.label_43.setObjectName("label_43")
        self.gridLayout_4.addWidget(self.label_43, 2, 1, 1, 1)
        self.horizontalLayout_4.addLayout(self.gridLayout_4)
        self.gridLayout_5.addWidget(self.frame_15, 2, 4, 1, 2)
        self.frame_9 = QtWidgets.QFrame(self.frame_2)
        self.frame_9.setFixedWidth(170)
        self.frame_9.setFrameShape(QtWidgets.QFrame.Box)
        self.frame_9.setFrameShadow(QtWidgets.QFrame.Plain)
        self.frame_9.setObjectName("frame_9")
        self.verticalLayout_3 = QtWidgets.QVBoxLayout(self.frame_9)
        self.verticalLayout_3.setContentsMargins(4, 4, 4, 4)
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.label_15 = QtWidgets.QLabel(self.frame_9)
        self.label_15.setMinimumSize(QtCore.QSize(150, 40))
        self.label_15.setMaximumSize(QtCore.QSize(150, 40))
        self.label_15.setAlignment(QtCore.Qt.AlignCenter)
        self.label_15.setObjectName("label_15")
        self.verticalLayout_3.addWidget(self.label_15)
        self.label_14 = QtWidgets.QLabel(self.frame_9)
        self.label_14.setMinimumSize(QtCore.QSize(150, 40))
        self.label_14.setMaximumSize(QtCore.QSize(150, 40))
        self.label_14.setText("")
        self.label_14.setObjectName("label_14")
        self.verticalLayout_3.addWidget(self.label_14)
        self.gridLayout_5.addWidget(self.frame_9, 1, 1, 1, 2)
        self.frame_5 = QtWidgets.QFrame(self.frame_2)
        self.frame_5.setFixedWidth(170)
        self.frame_5.setFrameShape(QtWidgets.QFrame.Box)
        self.frame_5.setFrameShadow(QtWidgets.QFrame.Plain)
        self.frame_5.setObjectName("frame_5")
        self.verticalLayout_15 = QtWidgets.QVBoxLayout(self.frame_5)
        self.verticalLayout_15.setContentsMargins(4, 4, 4, 4)
        self.verticalLayout_15.setObjectName("verticalLayout_15")
        self.label_6 = QtWidgets.QLabel(self.frame_5)
        self.label_6.setMinimumSize(QtCore.QSize(150, 40))
        self.label_6.setMaximumSize(QtCore.QSize(150, 40))
        self.label_6.setAlignment(QtCore.Qt.AlignCenter)
        self.label_6.setObjectName("label_6")
        self.verticalLayout_15.addWidget(self.label_6)
        self.label_7 = QtWidgets.QLabel(self.frame_5)
        self.label_7.setMinimumSize(QtCore.QSize(150, 40))
        self.label_7.setMaximumSize(QtCore.QSize(150, 40))
        self.label_7.setText("")
        self.label_7.setObjectName("label_7")
        self.verticalLayout_15.addWidget(self.label_7)
        self.gridLayout_5.addWidget(self.frame_5, 0, 3, 1, 1)
        self.frame_3 = QtWidgets.QFrame(self.frame_2)
        self.frame_3.setFixedWidth(170)
        self.frame_3.setFrameShape(QtWidgets.QFrame.Box)
        self.frame_3.setFrameShadow(QtWidgets.QFrame.Plain)
        self.frame_3.setObjectName("frame_3")
        self.verticalLayout_5 = QtWidgets.QVBoxLayout(self.frame_3)
        self.verticalLayout_5.setContentsMargins(4, 4, 4, 4)
        self.verticalLayout_5.setObjectName("verticalLayout_5")
        self.label_2 = QtWidgets.QLabel(self.frame_3)
        self.label_2.setFixedSize(150, 40)
        self.label_2.setAlignment(QtCore.Qt.AlignCenter)
        self.label_2.setObjectName("label_2")
        self.verticalLayout_5.addWidget(self.label_2)
        self.label_3 = QtWidgets.QLabel(self.frame_3)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_3.sizePolicy().hasHeightForWidth())
        self.label_3.setSizePolicy(sizePolicy)
        self.label_3.setMinimumSize(QtCore.QSize(150, 40))
        self.label_3.setMaximumSize(QtCore.QSize(150, 40))
        
        self.label_3.setText("")
        self.label_3.setObjectName("label_3")
        self.verticalLayout_5.addWidget(self.label_3)
        self.gridLayout_5.addWidget(self.frame_3, 0, 0, 1, 1)
        self.frame_8 = QtWidgets.QFrame(self.frame_2)
        self.frame_8.setFixedWidth(170)
        self.frame_8.setFrameShape(QtWidgets.QFrame.Box)
        self.frame_8.setFrameShadow(QtWidgets.QFrame.Plain)
        self.frame_8.setObjectName("frame_8")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(self.frame_8)
        self.verticalLayout_2.setContentsMargins(4, 4, 4, 4)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.label_13 = QtWidgets.QLabel(self.frame_8)
        self.label_13.setMinimumSize(QtCore.QSize(150, 40))
        self.label_13.setMaximumSize(QtCore.QSize(150, 40))
        self.label_13.setAlignment(QtCore.Qt.AlignCenter)
        self.label_13.setObjectName("label_13")
        self.verticalLayout_2.addWidget(self.label_13)
        self.label_12 = QtWidgets.QLabel(self.frame_8)
        self.label_12.setMinimumSize(QtCore.QSize(150, 40))
        self.label_12.setMaximumSize(QtCore.QSize(150, 40))
        self.label_12.setText("")
        self.label_12.setObjectName("label_12")
        self.verticalLayout_2.addWidget(self.label_12)
        self.gridLayout_5.addWidget(self.frame_8, 1, 0, 1, 1)
        self.frame_10 = QtWidgets.QFrame(self.frame_2)
        self.frame_10.setFixedWidth(170)
        self.frame_10.setFrameShape(QtWidgets.QFrame.Box)
        self.frame_10.setFrameShadow(QtWidgets.QFrame.Plain)
        self.frame_10.setObjectName("frame_10")
        self.verticalLayout_4 = QtWidgets.QVBoxLayout(self.frame_10)
        self.verticalLayout_4.setContentsMargins(4, 4, 4, 4)
        self.verticalLayout_4.setObjectName("verticalLayout_4")
        self.label_17 = QtWidgets.QLabel(self.frame_10)
        self.label_17.setMinimumSize(QtCore.QSize(150, 40))
        self.label_17.setMaximumSize(QtCore.QSize(150, 40))
        self.label_17.setAlignment(QtCore.Qt.AlignCenter)
        self.label_17.setObjectName("label_17")
        self.verticalLayout_4.addWidget(self.label_17)
        self.label_16 = QtWidgets.QLabel(self.frame_10)
        self.label_16.setMinimumSize(QtCore.QSize(150, 40))
        self.label_16.setMaximumSize(QtCore.QSize(150, 40))
        self.label_16.setText("")
        self.label_16.setObjectName("label_16")
        self.verticalLayout_4.addWidget(self.label_16)
        self.gridLayout_5.addWidget(self.frame_10, 1, 3, 1, 1)
        self.frame_13 = QtWidgets.QFrame(self.frame_2)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.frame_13.sizePolicy().hasHeightForWidth())
        self.frame_13.setSizePolicy(sizePolicy)
        self.frame_13.setMinimumSize(QtCore.QSize(230, 150))
        self.frame_13.setMaximumSize(QtCore.QSize(230, 150))
        self.frame_13.setFrameShape(QtWidgets.QFrame.Box)
        self.frame_13.setFrameShadow(QtWidgets.QFrame.Plain)
        self.frame_13.setObjectName("frame_13")
        self.horizontalLayout_5 = QtWidgets.QHBoxLayout(self.frame_13)
        self.horizontalLayout_5.setContentsMargins(4, 4, 4, 4)        
        self.horizontalLayout_5.setSpacing(9)
        self.horizontalLayout_5.setObjectName("horizontalLayout_5")
        self.gridLayout_2 = QtWidgets.QGridLayout()
        self.gridLayout_2.setContentsMargins(9, 9, 9, 9)
        self.gridLayout_2.setSpacing(9)
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.label_26 = QtWidgets.QLabel(self.frame_13)
        self.label_26.setAlignment(QtCore.Qt.AlignCenter)
        self.label_26.setObjectName("label_26")
        self.gridLayout_2.addWidget(self.label_26, 0, 0, 1, 1)
        self.label_27 = QtWidgets.QLabel(self.frame_13)
        self.label_27.setText("")
        self.label_27.setObjectName("label_27")
        self.gridLayout_2.addWidget(self.label_27, 0, 1, 1, 1)
        self.label_28 = QtWidgets.QLabel(self.frame_13)
        self.label_28.setAlignment(QtCore.Qt.AlignCenter)
        self.label_28.setObjectName("label_28")
        self.gridLayout_2.addWidget(self.label_28, 1, 0, 1, 1)
        self.label_29 = QtWidgets.QLabel(self.frame_13)
        self.label_29.setText("")
        self.label_29.setObjectName("label_29")
        self.gridLayout_2.addWidget(self.label_29, 1, 1, 1, 1)
        self.label_30 = QtWidgets.QLabel(self.frame_13)
        self.label_30.setAlignment(QtCore.Qt.AlignCenter)
        self.label_30.setObjectName("label_30")
        self.gridLayout_2.addWidget(self.label_30, 2, 0, 1, 1)
        self.label_31 = QtWidgets.QLabel(self.frame_13)
        self.label_31.setText("")
        self.label_31.setObjectName("label_31")
        self.gridLayout_2.addWidget(self.label_31, 2, 1, 1, 1)
        self.horizontalLayout_5.addLayout(self.gridLayout_2)
        self.gridLayout_5.addWidget(self.frame_13, 4, 4, 1, 2)
        self.frame_11 = QtWidgets.QFrame(self.frame_2)
        self.frame_11.setFixedWidth(170)
        self.frame_11.setStyleSheet("")
        self.frame_11.setFrameShape(QtWidgets.QFrame.Box)
        self.frame_11.setFrameShadow(QtWidgets.QFrame.Plain)
        self.frame_11.setObjectName("frame_11")
        self.verticalLayout_6 = QtWidgets.QVBoxLayout(self.frame_11)
        self.verticalLayout_6.setContentsMargins(4, 4, 4, 4)
        self.verticalLayout_6.setObjectName("verticalLayout_6")
        self.label_19 = QtWidgets.QLabel(self.frame_11)
        self.label_19.setMinimumSize(QtCore.QSize(150, 40))
        self.label_19.setMaximumSize(QtCore.QSize(150, 40))
        self.label_19.setAlignment(QtCore.Qt.AlignCenter)
        self.label_19.setObjectName("label_19")
        self.verticalLayout_6.addWidget(self.label_19)
        self.label_18 = QtWidgets.QLabel(self.frame_11)
        self.label_18.setMinimumSize(QtCore.QSize(150, 40))
        self.label_18.setMaximumSize(QtCore.QSize(150, 40))
        self.label_18.setText("")
        self.label_18.setObjectName("label_18")
        self.verticalLayout_6.addWidget(self.label_18)
        self.gridLayout_5.addWidget(self.frame_11, 1, 4, 1, 1)
        self.frame_14 = QtWidgets.QFrame(self.frame_2)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.frame_14.sizePolicy().hasHeightForWidth())
        self.frame_14.setSizePolicy(sizePolicy)
        self.frame_14.setFixedSize(230, 150)
        self.frame_14.setFrameShape(QtWidgets.QFrame.Box)
        self.frame_14.setFrameShadow(QtWidgets.QFrame.Plain)
        self.frame_14.setObjectName("frame_14")
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout(self.frame_14)
        self.horizontalLayout_3.setContentsMargins(4, 4, 4, 4)
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.gridLayout_3 = QtWidgets.QGridLayout()
        self.gridLayout_3.setContentsMargins(9, 9, 9, 9)
        self.gridLayout_3.setSpacing(9)
        self.gridLayout_3.setObjectName("gridLayout_3")
        self.label_32 = QtWidgets.QLabel(self.frame_14)
        self.label_32.setAlignment(QtCore.Qt.AlignCenter)
        self.label_32.setObjectName("label_32")
        self.gridLayout_3.addWidget(self.label_32, 0, 0, 1, 1)
        self.label_33 = QtWidgets.QLabel(self.frame_14)
        self.label_33.setText("")
        self.label_33.setObjectName("label_33")
        self.gridLayout_3.addWidget(self.label_33, 0, 1, 1, 1)
        self.label_34 = QtWidgets.QLabel(self.frame_14)
        self.label_34.setAlignment(QtCore.Qt.AlignCenter)
        self.label_34.setObjectName("label_34")
        self.gridLayout_3.addWidget(self.label_34, 1, 0, 1, 1)
        self.label_35 = QtWidgets.QLabel(self.frame_14)
        self.label_35.setText("")
        self.label_35.setObjectName("label_35")
        self.gridLayout_3.addWidget(self.label_35, 1, 1, 1, 1)
        self.label_36 = QtWidgets.QLabel(self.frame_14)
        self.label_36.setAlignment(QtCore.Qt.AlignCenter)
        self.label_36.setObjectName("label_36")
        self.gridLayout_3.addWidget(self.label_36, 2, 0, 1, 1)
        self.label_37 = QtWidgets.QLabel(self.frame_14)
        self.label_37.setText("")
        self.label_37.setObjectName("label_37")
        self.gridLayout_3.addWidget(self.label_37, 2, 1, 1, 1)
        self.horizontalLayout_3.addLayout(self.gridLayout_3)
        self.gridLayout_5.addWidget(self.frame_14, 2, 0, 1, 2)
        self.frame_6 = QtWidgets.QFrame(self.frame_2)
        self.frame_6.setFixedWidth(170)
        self.frame_6.setFrameShape(QtWidgets.QFrame.Box)
        self.frame_6.setFrameShadow(QtWidgets.QFrame.Plain)
        self.frame_6.setObjectName("frame_6")
        self.verticalLayout_16 = QtWidgets.QVBoxLayout(self.frame_6)
        self.verticalLayout_16.setContentsMargins(4, 4, 4, 4)
        self.verticalLayout_16.setObjectName("verticalLayout_16")
        self.label_9 = QtWidgets.QLabel(self.frame_6)
        self.label_9.setMinimumSize(QtCore.QSize(150, 40))
        self.label_9.setMaximumSize(QtCore.QSize(150, 40))
        self.label_9.setAlignment(QtCore.Qt.AlignCenter)
        self.label_9.setObjectName("label_9")
        self.verticalLayout_16.addWidget(self.label_9)
        self.label_8 = QtWidgets.QLabel(self.frame_6)
        self.label_8.setMinimumSize(QtCore.QSize(150, 40))
        self.label_8.setMaximumSize(QtCore.QSize(150, 40))
        self.label_8.setText("")
        self.label_8.setObjectName("label_8")
        self.verticalLayout_16.addWidget(self.label_8)
        self.gridLayout_5.addWidget(self.frame_6, 0, 4, 1, 1)
        self.gridLayout_5.addWidget(self.stl_view, 2, 2, 3, 2)
        self.stl_view.setSizePolicy(
    QtWidgets.QSizePolicy.Expanding,
    QtWidgets.QSizePolicy.Expanding
)

        '''self.label = QtWidgets.QLabel(self.frame_2)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label.sizePolicy().hasHeightForWidth())
        self.label.setSizePolicy(sizePolicy)
        self.label.setMinimumSize(QtCore.QSize(0, 0))
        self.label.setMaximumSize(QtCore.QSize(16777215, 16777215))
        self.label.setStyleSheet("QLabel#label{\n"
"background-color: transparent;\n"
"border:none;\n"
"}")
        self.label.setText("")
        self.label.setPixmap(QtGui.QPixmap(":/icons/Rocket.gif"))
        self.label.setFixedSize(300, 300)
        self.label.setScaledContents(True)
        self.label.setObjectName("label")
        
        #QMovie for animated gif
        
        self.movie = QMovie(":/icons/Rocket.gif")  # or "Rocket.gif" if in same folder
        self.label.setMovie(self.movie)
        self.movie.start()
        self.gridLayout_5.addWidget(self.label, 2, 2, 3, 2)'''
        spacerItem = QtWidgets.QSpacerItem(20, 18, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.gridLayout_5.addItem(spacerItem, 3, 0, 1, 1)
        spacerItem1 = QtWidgets.QSpacerItem(20, 24, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.gridLayout_5.addItem(spacerItem1, 3, 4, 1, 1)
        self.frame_4 = QtWidgets.QFrame(self.frame_2)
        self.frame_4.setFixedWidth(170)
        self.frame_4.setFrameShape(QtWidgets.QFrame.Box)
        self.frame_4.setFrameShadow(QtWidgets.QFrame.Plain)
        self.frame_4.setObjectName("frame_4")
        self.verticalLayout_14 = QtWidgets.QVBoxLayout(self.frame_4)
        self.verticalLayout_14.setContentsMargins(4, 4, 4, 4)
        self.verticalLayout_14.setObjectName("verticalLayout_14")
        self.label_4 = QtWidgets.QLabel(self.frame_4)
        self.label_4.setMinimumSize(QtCore.QSize(150, 40))
        self.label_4.setMaximumSize(QtCore.QSize(150, 40))
        self.label_4.setAlignment(QtCore.Qt.AlignCenter)
        self.label_4.setObjectName("label_4")
        self.verticalLayout_14.addWidget(self.label_4)
        self.label_5 = QtWidgets.QLabel(self.frame_4)
        self.label_5.setMinimumSize(QtCore.QSize(150, 40))
        self.label_5.setMaximumSize(QtCore.QSize(150, 40))
        self.label_5.setText("")
        self.label_5.setObjectName("label_5")
        self.verticalLayout_14.addWidget(self.label_5)
        self.gridLayout_5.addWidget(self.frame_4, 0, 1, 1, 2)
        self.frame_7 = QtWidgets.QFrame(self.frame_2)
        self.frame_7.setFixedWidth(170)
        self.frame_7.setFrameShape(QtWidgets.QFrame.Box)
        self.frame_7.setFrameShadow(QtWidgets.QFrame.Plain)
        self.frame_7.setObjectName("frame_7")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.frame_7)
        self.verticalLayout.setContentsMargins(4, 4, 4, 4)
        self.verticalLayout.setObjectName("verticalLayout")
        self.label_11 = QtWidgets.QLabel(self.frame_7)
        self.label_11.setMinimumSize(QtCore.QSize(150, 40))
        self.label_11.setMaximumSize(QtCore.QSize(150, 40))
        self.label_11.setAlignment(QtCore.Qt.AlignCenter)
        self.label_11.setObjectName("label_11")
        self.verticalLayout.addWidget(self.label_11)
        self.label_10 = QtWidgets.QLabel(self.frame_7)
        self.label_10.setMinimumSize(QtCore.QSize(150, 40))
        self.label_10.setMaximumSize(QtCore.QSize(150, 40))
        self.label_10.setText("")
        self.label_10.setObjectName("label_10")
        self.verticalLayout.addWidget(self.label_10)
        self.gridLayout_5.addWidget(self.frame_7, 0, 5, 1, 1)
        self.frame_12 = QtWidgets.QFrame(self.frame_2)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.frame_12.sizePolicy().hasHeightForWidth())
        self.frame_12.setSizePolicy(sizePolicy)
        self.frame_12setFixedSize(230, 150)
        self.frame_12.setFrameShape(QtWidgets.QFrame.Box)
        self.frame_12.setFrameShadow(QtWidgets.QFrame.Plain)
        self.frame_12.setObjectName("frame_12")
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout(self.frame_12)
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.gridLayout_8 = QtWidgets.QGridLayout()
        self.gridLayout_8.setContentsMargins(9, 9, 9, 9)
        self.gridLayout_8.setSpacing(9)
        self.gridLayout_8.setObjectName("gridLayout_8")
        self.label_20 = QtWidgets.QLabel(self.frame_12)
        self.label_20.setAlignment(QtCore.Qt.AlignCenter)
        self.label_20.setObjectName("label_20")
        self.gridLayout_8.addWidget(self.label_20, 0, 0, 1, 1)
        self.label_21 = QtWidgets.QLabel(self.frame_12)
        self.label_21.setText("")
        self.label_21.setObjectName("label_21")
        self.gridLayout_8.addWidget(self.label_21, 0, 1, 1, 1)
        self.label_22 = QtWidgets.QLabel(self.frame_12)
        self.label_22.setAlignment(QtCore.Qt.AlignCenter)
        self.label_22.setObjectName("label_22")
        self.gridLayout_8.addWidget(self.label_22, 1, 0, 1, 1)
        self.label_24 = QtWidgets.QLabel(self.frame_12)
        self.label_24.setText("")
        self.label_24.setObjectName("label_24")
        self.gridLayout_8.addWidget(self.label_24, 1, 1, 1, 1)
        self.label_23 = QtWidgets.QLabel(self.frame_12)
        self.label_23.setAlignment(QtCore.Qt.AlignCenter)
        self.label_23.setObjectName("label_23")
        self.gridLayout_8.addWidget(self.label_23, 2, 0, 1, 1)
        self.label_25 = QtWidgets.QLabel(self.frame_12)
        self.label_25.setText("")
        self.label_25.setObjectName("label_25")
        self.gridLayout_8.addWidget(self.label_25, 2, 1, 1, 1)
        self.horizontalLayout_2.addLayout(self.gridLayout_8)
        self.gridLayout_5.addWidget(self.frame_12, 4, 0, 1, 2, QtCore.Qt.AlignTop)
        self.gridLayout_7.addLayout(self.gridLayout_5, 0, 0, 1, 1)
        self.gridLayout_5.setColumnStretch(0, 1)
        self.gridLayout_5.setColumnStretch(1, 1)
        self.gridLayout_5.setColumnStretch(2, 2)  # STL view area
        self.gridLayout_5.setColumnStretch(3, 1)
        self.gridLayout_5.setColumnStretch(4, 1)
        self.gridLayout_5.setColumnStretch(5, 1)
        self.frame_16 = QtWidgets.QFrame(self.frame_2)
        self.frame_16.setMinimumSize(QtCore.QSize(200, 500))
        self.frame_16.setMaximumSize(QtCore.QSize(16777215, 16777215))
        self.frame_16.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.frame_16.setFrameShadow(QtWidgets.QFrame.Plain)
        self.frame_16.setObjectName("frame_16")
        self.verticalLayout_10 = QtWidgets.QVBoxLayout(self.frame_16)
        self.verticalLayout_10.setObjectName("verticalLayout_10")
        self.frame_24 = QtWidgets.QFrame(self.frame_16)
        self.frame_24.setMinimumSize(QtCore.QSize(150, 50))
        self.frame_24.setMaximumSize(QtCore.QSize(16777215, 16777215))
        self.frame_24.setFrameShape(QtWidgets.QFrame.Box)
        self.frame_24.setFrameShadow(QtWidgets.QFrame.Plain)
        self.frame_24.setObjectName("frame_24")
        self.verticalLayout_13 = QtWidgets.QVBoxLayout(self.frame_24)
        self.verticalLayout_13.setObjectName("verticalLayout_13")
        self.label_44 = QtWidgets.QLabel(self.frame_24)
        self.label_44.setFixedHeight(40)
        self.label_44.setObjectName("label_44")
        self.verticalLayout_13.addWidget(self.label_44)
        self.verticalLayout_10.addWidget(self.frame_24)
        self.frame_17 = QtWidgets.QFrame(self.frame_16)
        self.frame_17.setFrameShape(QtWidgets.QFrame.Box)
        self.frame_17.setFrameShadow(QtWidgets.QFrame.Plain)
        self.frame_17.setObjectName("frame_17")
        self.verticalLayout_7 = QtWidgets.QVBoxLayout(self.frame_17)
        self.verticalLayout_7.setObjectName("verticalLayout_7")
        self.label_51 = QtWidgets.QLabel(self.frame_17)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_51.sizePolicy().hasHeightForWidth())
        self.label_51.setSizePolicy(sizePolicy)
        self.label_51.setAlignment(QtCore.Qt.AlignCenter)
        self.label_51.setObjectName("label_51")
        self.verticalLayout_7.addWidget(self.label_51)
        self.progressBar_7 = QtWidgets.QProgressBar(self.frame_17)
        self.progressBar_7.setMinimumSize(QtCore.QSize(110, 15))
        self.progressBar_7.setStyleSheet("")
        self.progressBar_7.setMinimum(24)
        self.progressBar_7.setMaximum(100)
        self.progressBar_7.setProperty("value", 0)
        self.progressBar_7.setObjectName("progressBar_7")
        self.verticalLayout_7.addWidget(self.progressBar_7)
        self.verticalLayout_10.addWidget(self.frame_17)
        self.frame_18 = QtWidgets.QFrame(self.frame_16)
        self.frame_18.setFrameShape(QtWidgets.QFrame.Box)
        self.frame_18.setFrameShadow(QtWidgets.QFrame.Plain)
        self.frame_18.setObjectName("frame_18")
        self.verticalLayout_8 = QtWidgets.QVBoxLayout(self.frame_18)
        self.verticalLayout_8.setObjectName("verticalLayout_8")
        self.label_52 = QtWidgets.QLabel(self.frame_18)
        self.label_52.setAlignment(QtCore.Qt.AlignCenter)
        self.label_52.setObjectName("label_52")
        self.verticalLayout_8.addWidget(self.label_52)
        self.progressBar_8 = QtWidgets.QProgressBar(self.frame_18)
        self.progressBar_8.setMinimumSize(QtCore.QSize(110, 15))
        self.progressBar_8.setStyleSheet("")
        self.progressBar_8.setMaximum(100)
        self.progressBar_8.setProperty("value", 0)
        self.progressBar_8.setObjectName("progressBar_8")
        self.verticalLayout_8.addWidget(self.progressBar_8)
        self.verticalLayout_10.addWidget(self.frame_18)
        self.frame_22 = QtWidgets.QFrame(self.frame_16)
        self.frame_22.setFrameShape(QtWidgets.QFrame.Box)
        self.frame_22.setFrameShadow(QtWidgets.QFrame.Plain)
        self.frame_22.setObjectName("frame_22")
        self.verticalLayout_12 = QtWidgets.QVBoxLayout(self.frame_22)
        self.verticalLayout_12.setObjectName("verticalLayout_12")
        self.label_56 = QtWidgets.QLabel(self.frame_22)
        self.label_56.setAlignment(QtCore.Qt.AlignCenter)
        self.label_56.setObjectName("label_56")
        self.verticalLayout_12.addWidget(self.label_56)
        self.progressBar_12 = QtWidgets.QProgressBar(self.frame_22)
        self.progressBar_12.setMinimumSize(QtCore.QSize(110, 15))
        self.progressBar_12.setStyleSheet("")
        self.progressBar_12.setProperty("value", 0)
        self.progressBar_12.setObjectName("progressBar_12")
        self.verticalLayout_12.addWidget(self.progressBar_12)
        self.verticalLayout_10.addWidget(self.frame_22)
        self.frame_19 = QtWidgets.QFrame(self.frame_16)
        self.frame_19.setFrameShape(QtWidgets.QFrame.Box)
        self.frame_19.setFrameShadow(QtWidgets.QFrame.Plain)
        self.frame_19.setObjectName("frame_19")
        self.verticalLayout_9 = QtWidgets.QVBoxLayout(self.frame_19)
        self.verticalLayout_9.setObjectName("verticalLayout_9")
        self.label_53 = QtWidgets.QLabel(self.frame_19)
        self.label_53.setAlignment(QtCore.Qt.AlignCenter)
        self.label_53.setObjectName("label_53")
        self.verticalLayout_9.addWidget(self.label_53)
        self.progressBar_9 = QtWidgets.QProgressBar(self.frame_19)
        self.progressBar_9.setMinimumSize(QtCore.QSize(110, 15))
        self.progressBar_9.setStyleSheet("")
        self.progressBar_9.setProperty("value", 0)
        self.progressBar_9.setObjectName("progressBar_9")
        self.verticalLayout_9.addWidget(self.progressBar_9)
        self.verticalLayout_10.addWidget(self.frame_19)
        self.frame_21 = QtWidgets.QFrame(self.frame_16)
        self.frame_21.setFrameShape(QtWidgets.QFrame.Box)
        self.frame_21.setFrameShadow(QtWidgets.QFrame.Plain)
        self.frame_21.setObjectName("frame_21")
        self.verticalLayout_11 = QtWidgets.QVBoxLayout(self.frame_21)
        self.verticalLayout_11.setObjectName("verticalLayout_11")
        self.label_55 = QtWidgets.QLabel(self.frame_21)
        self.label_55.setAlignment(QtCore.Qt.AlignCenter)
        self.label_55.setObjectName("label_55")
        self.verticalLayout_11.addWidget(self.label_55)
        self.progressBar_11 = QtWidgets.QProgressBar(self.frame_21)
        self.progressBar_11.setMinimumSize(QtCore.QSize(110, 15))
        self.progressBar_11.setStyleSheet("")
        self.progressBar_11.setProperty("value", 0)
        self.progressBar_11.setObjectName("progressBar_11")
        self.verticalLayout_11.addWidget(self.progressBar_11)
        self.verticalLayout_10.addWidget(self.frame_21)
        self.gridLayout_7.addWidget(self.frame_16, 0, 1, 1, 1)
        self.gridLayout_6.addLayout(self.gridLayout_7, 0, 0, 1, 1)
        self.gridLayout_9.addWidget(self.frame_2, 0, 0, 1, 1)
        self.gridLayout_9.setColumnStretch(0, 3)
        self.gridLayout_9.setRowStretch(0, 1)
        self.gridLayout.addWidget(self.rootFrame, 0, 0, 1, 1)
        self.retranslateUi(Form) 
        QtCore.QMetaObject.connectSlotsByName(Form)
        
    def retranslateUi(self, Form):
        _translate = QtCore.QCoreApplication.translate
        Form.setWindowTitle(_translate("Form", "Form"))
        self.label_38.setText(_translate("Form", "Gyro  X"))
        self.label_40.setText(_translate("Form", "Gyro  Y"))
        self.label_42.setText(_translate("Form", "Gyro  Z"))
        self.label_15.setText(_translate("Form", "Load Current "))
        self.label_6.setText(_translate("Form", "Packet Count"))
        self.label_2.setText(_translate("Form", "Rocket ID"))
        self.label_13.setText(_translate("Form", "Load Voltage"))
        self.label_17.setText(_translate("Form", "GPS Latitude"))
        self.label_26.setText(_translate("Form", "Euler X"))
        self.label_28.setText(_translate("Form", "Euler Y"))
        self.label_30.setText(_translate("Form", "Euler  Z"))
        self.label_19.setText(_translate("Form", "GPS Longitude"))
        self.label_32.setText(_translate("Form", "Accel  X"))
        self.label_34.setText(_translate("Form", "Accel Y"))
        self.label_36.setText(_translate("Form", "Accel  Z"))
        self.label_9.setText(_translate("Form", "Altitude"))
        self.label_4.setText(_translate("Form", "Mission Time"))
        self.label_11.setText(_translate("Form", "Pressure"))
        self.label_20.setText(_translate("Form", "Mag X"))
        self.label_22.setText(_translate("Form", "Mag  Y"))
        self.label_23.setText(_translate("Form", "Mag Z"))
        self.label_44.setText(_translate("Form", " State: "))
        self.label_51.setText(_translate("Form", "Battery "))
        self.label_52.setText(_translate("Form", "Altitude"))
        self.label_56.setText(_translate("Form", "Power Consumption"))
        self.label_53.setText(_translate("Form", "Load Voltage"))
        self.label_55.setText(_translate("Form", "Pressure"))
        
        
    @QtCore.pyqtSlot(str)
    @QtCore.pyqtSlot(object)
    def update_data(self, data):

        current_time = QtCore.QDateTime.currentMSecsSinceEpoch()

        if current_time - self.last_update_time < self.update_interval_ms:
            return

        self.last_update_time = current_time

        try:
            values = data.strip().split(",")

            if len(values) < len(self.telemetry_fields):
                return

            telemetry = dict(zip(self.telemetry_fields, values))

            # ---------------- Update Labels ----------------
            for field, widget in self.field_widgets.items():
                if field in telemetry and isinstance(widget, QtWidgets.QLabel):
                    widget.setText(str(telemetry[field]))

            # ---------------- Convert Telemetry ----------------
            altitude = float(telemetry.get("Altitude", 0))
            pressure = float(telemetry.get("Pressure", 0))
            voltage = float(telemetry.get("Load Voltage", 0))
            current = float(telemetry.get("Load Current", 0))

            # ---------------- Power Calculation ----------------
            power = voltage * current

            # ---------------- Battery Calculation ----------------
            now = QtCore.QDateTime.currentMSecsSinceEpoch()
            dt = (now - self.last_energy_time) / 3600000.0
            self.last_energy_time = now

            self.total_energy_Wh += power * dt

            remaining_energy = max(0, self.battery_capacity_Wh - self.total_energy_Wh)
            battery_percent = int((remaining_energy / self.battery_capacity_Wh) * 100)

            # ---------------- Percent Calculations ----------------
            altitude_percent = int((altitude / 1000) * 100)
            pressure_percent = int((pressure / 1100) * 100)
            power_percent = int((power / 50) * 100)

            # Clamp values
            altitude_percent = max(0, min(100, altitude_percent))
            pressure_percent = max(0, min(100, pressure_percent))
            power_percent = max(0, min(100, power_percent))
            battery_percent = max(0, min(100, battery_percent))
            voltage_percent = int((voltage / 12) * 100)
            voltage_percent = max(0, min(100, voltage_percent))

            # ---------------- Update Progress Bars ----------------

            # Battery
            self.progressBar_7.setRange(0,100)
            self.progressBar_7.setValue(battery_percent)

            # Altitude
            self.progressBar_8.setRange(0,100)
            self.progressBar_8.setValue(altitude_percent)
            
            self.progressBar_9.setRange(0,100)
            self.progressBar_9.setValue(voltage_percent)

            # Pressure
            self.progressBar_11.setRange(0,100)
            self.progressBar_11.setValue(pressure_percent)

            # Power
            self.progressBar_12.setRange(0,100)
            self.progressBar_12.setValue(power_percent)

        except Exception as e:
            print("Telemetry parse error:", e)


    def parse(self, line):
        try:
            return dict(item.split(":") for item in line.split(","))
        except:
            return None

    def on_serial_data(self, data):
        try:
            # Split multiple fields
            parts = data.split(",")
            for part in parts:
                if ":" not in part:
                    continue

                key, value = part.split(":", 1)
                key = key.strip()
                value = value.strip()

                if key in self.field_widgets:
                    widgets = self.field_widgets[key]

                    # -----------------
                    # Update Label
                    # -----------------
                    if "label" in widgets:
                        widgets["label"].setText(value)

                    # -----------------
                    # Update ProgressBar
                    # -----------------
                    if "progress" in widgets:
                        try:
                            numeric_value = int(float(value))
                            # Optional: clamp within range
                            progress = widgets["progress"]
                            min_val = progress.minimum()
                            max_val = progress.maximum()
                            numeric_value = max(min_val, min(numeric_value, max_val))
                            progress.setValue(numeric_value)
                        except ValueError:
                            pass  # ignore if not numeric
        except Exception as e:
            print("Serial update error:", e)


    def update_stl_from_serial(self, data):
        try:
            if isinstance(data, dict):
                roll = float(data.get("roll", 0))
                pitch = float(data.get("pitch", 0))
                yaw = float(data.get("yaw", 0))
            else:
                parts = data.strip().split(",")
                if len(parts) < 21:
                    return
                roll = float(parts[18])
                pitch = float(parts[19])
                yaw = float(parts[20])

            self.stl_view.update_orientation({
                "roll": roll,
                "pitch": pitch,
                "yaw": yaw
            })
        except Exception as e:
            print("DB STL error:", e)

        
'''if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    ui = DbWindow()   # DbWindow IS the widget
    ui.show()
    sys.exit(app.exec_())'''
