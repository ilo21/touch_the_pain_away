# # import serial
import time
import struct
import os
import datetime
import PyQt5
from PyQt5 import QtGui, QtCore
from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt, pyqtSignal, pyqtSlot
from statistics import mean 


LOG_FOLDER = "_PUMP_THRESHOLD_LOGs"
PUMP_DATA_LOG_FILE = "pump_data.txt"
# baudrate from pump spec file
BAUDRATE = 115200    
# how often pump sends a value
SAMPLE_RATE_MS = 100 
TARGET_PRESSURE_HOLD_TIME_SEC = 5
MAX_PRESSURE = 117
# from  pump spec file: 1 = start code  , 255 = stop code
COMMAND_START_CODE = 1                           
COMMAND_STOP_CODE = 255     
NO_TRIALS = 3
WAIT_DEFLATE = 4000
###############################################################################
# MY APP CLASSES

class MySettingsWidget(QMainWindow):

    valid_input_sig = pyqtSignal()
    def __init__(self):
        super(MySettingsWidget, self).__init__()
        self.name = "Test Settings"
        self.app_width = 400
        self.app_height = 80
        self.setWindowTitle(self.name)
        self.resize(self.app_width,self.app_height)

        self.participant_id = ""
        self.com_port = ""
        

        self.main_widget = QWidget()
        self.main_layout = QFormLayout()
        self.setCentralWidget(self.main_widget)       
        self.main_widget.setLayout(self.main_layout)
        self.participant_id_label = QLabel("Participant ID:")
        self.participant_id_text = QLineEdit("1")
        self.participant_id_text.setValidator(QtGui.QIntValidator())
        self.main_layout.addRow(self.participant_id_label,self.participant_id_text)
        self.select_com_port_label = QLabel("Select USB port for the Pump:")
        self.select_com_port_label_text = QLineEdit("COM4")
        self.main_layout.addRow(self.select_com_port_label,self.select_com_port_label_text)

        self.start_btn = QPushButton("Start")
        self.main_layout.addRow("",self.start_btn)

        self.start_btn.clicked.connect(self.read_user_input)
        self.valid_input_sig.connect(self.start_task)
        

    def read_user_input(self):
        self.com_port = self.select_com_port_label_text.text()
        try:
            self.participant_id = int(self.participant_id_text.text())
            self.valid_input_sig.emit()
        except:
            print("Wrong value entered.")
            self.show_info_dialog("Wrong value entered.")

    @pyqtSlot()
    def start_task(self):
        self.close()
        self.task_presentation = PresentationWidget([self.participant_id,self.com_port])
        self.task_presentation.showMaximized()
        # self.task_presentation.show()

     # show info that only ins are streamed
    def show_info_dialog(self, text):
        msgBox = QMessageBox()
        msgBox.setText(text)
        msgBox.setWindowTitle("Info!")
        msgBox.setWindowIcon(QtGui.QIcon(ICO))
        msgBox.setStandardButtons(QMessageBox.Ok)
        msgBox.exec()
####### end MyMainWidget class

########################################
# PRESENTATION CLASS
######################################

class PresentationWidget(QMainWindow):

    stop_pump_signal = pyqtSignal()
    wait_signal = pyqtSignal()
    apply_pain_signal = pyqtSignal()
    def __init__(self,params):
        super(PresentationWidget, self).__init__()
        self.name = "Test"
        self.app_width = 800
        self.app_height = 600
        self.setWindowTitle(self.name)
        self.resize(self.app_width,self.app_height)
        # changing the background color to black 
        self.setStyleSheet("background-color: black;") 


        # from user input
        self.participant_id = params[0]
        self.com_port = params[1]

        self.thresholds = []
        self.trial = 0

        # configure logging
        self.current_path = os.path.dirname(os.path.abspath(__file__))
        self.dump_path = os.path.join(self.current_path,LOG_FOLDER)
        try: 
            os.mkdir(self.dump_path)
        except:
            # print("Path exists")
            pass
        self.log_file_name = str(self.participant_id)+"_participant_"+datetime.datetime.now().strftime("%Y_%m_%d_%H_%M_%S")+".txt"
        self.log_path = os.path.join(self.dump_path,self.log_file_name)

        # log task settings
        f = open(self.log_path, "a")
        f.write("Participant ID: "+str(self.participant_id)+"\n\n")
        f.close()

        # keep track of what is displayed
        self.start_on = True
        self.threshold_on = False
        self.apply_pain = False

        self.main_widget = QWidget()
        self.main_layout = QVBoxLayout()
        self.setCentralWidget(self.main_widget)
        self.main_widget.setLayout(self.main_layout)
        self.init_widget = QWidget()
        self.init_layout = QVBoxLayout()
        self.info_label = QLabel("Tryck på B\nför att börja")
        self.info_label.setAlignment(Qt.AlignCenter)
        self.init_layout.addWidget(self.info_label)
        self.init_widget.setLayout(self.init_layout)
        self.main_layout.addWidget(self.init_widget)
    
        # make big label
        self.big_label_stylesheet = "QLabel {margin: 30px;font-size: 70pt;color:white}"
        self.init_widget.setStyleSheet(self.big_label_stylesheet)

        # connect signal
        self.stop_pump_signal.connect(self.write_pump_data)
        self.wait_signal.connect(self.wait)
        self.apply_pain_signal.connect(self.pump_apply_pain)

    # define keypress events
    def keyPressEvent(self,event):
        # wait for B before starting threshold measures
        if event.key() == Qt.Key_B and self.start_on == True:
            self.start_on = False
            self.start_threshold_measure()
        # wait for Spacebar to stop the pump
        elif event.key() == Qt.Key_Space and self.threshold_on == True:
            print("Stop pumping")
            self.stop_pump_signal.emit()
        # wait for S to start pain
        elif event.key() == Qt.Key_S and self.apply_pain == True:
            self.apply_pain_signal.emit()
            
        super(PresentationWidget, self).keyPressEvent(event)

    def start_threshold_measure(self):
        if self.trial < NO_TRIALS:
            self.threshold_on = True
            stop_widget = QWidget()
            stop_layout = QVBoxLayout()
            stop_label = QLabel("Tryck på Spacebar\nför att stoppa pumpen")
            stop_label.setAlignment(Qt.AlignCenter)
            stop_label.setStyleSheet(self.big_label_stylesheet)
            stop_layout.addWidget(stop_label)
            stop_widget.setLayout(stop_layout)
            self.main_layout.replaceWidget(self.init_widget,stop_widget)
            self.init_widget.deleteLater()
            self.init_widget = stop_widget
            # bytes read from pump
            # self.pumpBytes = bytearray([])
            # # initialize serial      
            # if not serial.Serial(self.com_port, BAUDRATE, timeout = 0.5).is_open:   
            #     # print("Port was closed")                           
            #     self.pumpController = serial.Serial(self.com_port, BAUDRATE, timeout = 0.5) 
            # else:
            #     # print("Port was already opened") 
            #     serial.Serial(self.com_port, BAUDRATE, timeout = 0.5).close()  
            #     self.pumpController = serial.Serial(self.com_port, BAUDRATE, timeout = 0.5) 
            #         
            # # This is the rate of inflation and speed of the motor. 
            # # It progresses stepwise where this value indicates 
            # # how many seconds it remains on this step before accelerating again. 
            # # Value is in seconds. This is required for the motor to be able to handle 
            # # the pressure inside the system, otherwise it would slow down to a halt.                                 
            # outputLevel = 3                                                  
            # # prepare the start and stop bytes
            # start_command_list = [ord('S'), COMMAND_START_CODE, MAX_PRESSURE, outputLevel, 1, 0]
            # # to start the pump
            # # send one command at a time with a delay in order for the pump not to miss anything
            # for i in range(len(start_command_list)):
            #     self.pumpController.write(bytearray([start_command_list[i]]))
            #     time.sleep(0.02)
            # # log time when pump starts sending data
            # self.send_pump_start_command_time = datetime.datetime.now()
            self.send_pump_start_command_time = datetime.datetime.now()
            self.trial +=1
        else:
            self.apply_pain = True
            self.prepare_pain()

    @pyqtSlot()
    def write_pump_data(self):
        self.threshold_on = False
        try:
            # # stop the pump
            # commandStop = bytearray([ord('S'), COMMAND_STOP_CODE, 0, 0, 0, 0])
            # self.pumpController.write(commandStop)
            # send a signal to wait for pump to deflate
            self.wait_signal.emit()
        except:
                print("ups")

    @pyqtSlot()
    def wait(self):
        
        wait_widget = QWidget()
        wait_layout = QVBoxLayout()
        wait_label = QLabel("Vänta")
        wait_label.setAlignment(Qt.AlignCenter)
        wait_label.setStyleSheet(self.big_label_stylesheet)
        wait_layout.addWidget(wait_label)
        wait_widget.setLayout(wait_layout)
        self.main_layout.replaceWidget(self.init_widget,wait_widget)
        self.init_widget.deleteLater()
        self.init_widget = wait_widget

        #################################
        # WRITE PUMP DATA TO A FILE
        # read all data that was sent by the pump
        # pump_data= self.pumpController.read(size=self.pumpController.in_waiting)
        # if len(pump_data) > 0:
        #     self.pumpBytes += bytearray(pump_data)
        #     # what the bytes look like unmodified 
        #     self.pumpBytes = struct.unpack( "=" + "B" * len(self.pumpBytes), self.pumpBytes)
        #
        # previous_t = self.send_pump_start_command_time   
        # if len(self.pumpBytes) != 0:   
        #     # create files for pump data
        #     self.pump_data_file_name = self.log_file_name.split(".")[0]+"_pump"+"Trial"+str(self.trial)+".txt"
        #     pump_data_dump = open(os.path.join(self.dump_path,self.pump_data_file_name),"w")
        #     self.pump_Hg_data_file_name = self.log_file_name.split(".")[0]+"_pumpHg"+"Trial"+str(self.trial)+".txt"
        #     pump_Hg_data_dump = open(os.path.join(self.dump_path,self.pump_Hg_data_file_name),"w")
        #     for i in range(0,len(self.pumpBytes)):
        #         previous_t_text = previous_t.strftime("%Y-%m-%d %H:%M:%S.%f")
        #         row_pump_data = previous_t_text + "    " + str(self.pumpBytes[i]) + "\n"
        #         pump_data_dump.write(row_pump_data)
        #         row_pump_dataHg =  previous_t_text + "    " + str(float(self.pumpBytes[i])*1.01372549) + "\n"
        #         pump_Hg_data_dump.write(row_pump_dataHg)
        #         # pump sends value every 100ms, therefore samples should be 100ms apart
        #         tt = previous_t + datetime.timedelta(milliseconds=SAMPLE_RATE_MS)
        #         previous_t = tt
        #     pump_data_dump.close()
        #     pump_Hg_data_dump.close()
        #     # save threshold
        #     current_threshold = self.pumpBytes[i]
        #     current_threshold_mmHg =float(self.pumpBytes[i])*1.01372549
        #     self.thresholds.append(current_threshold)
        #     print("Thresholds",self.thresholds)
        #     # write that to main log file
        #     f = open(self.log_path, "a")
        #     f.write("Threshold " + str(self.trial)+":    "+str(current_threshold)+"\n")
        #     f.write("Threshold " + str(self.trial)+":    "+str(current_threshold_mmHg)+" mmHg\n\n")
        #     f.close()
        # else:
        #     # print("No valid data found :(")
        #     pass
        # # close serial connection
        # self.pumpController.close()
        # wait a bit before next pumping
        PyQt5.QtCore.QTimer.singleShot(WAIT_DEFLATE, self.start_threshold_measure)

    def prepare_pain(self):
        pain_widget = QWidget()
        pain_layout = QVBoxLayout()
        pain_label = QLabel("Tryck på S\nför att bekräfta smärta")
        pain_label.setAlignment(Qt.AlignCenter)
        pain_label.setStyleSheet(self.big_label_stylesheet)
        pain_layout.addWidget(pain_label)
        pain_widget.setLayout(pain_layout)
        self.main_layout.replaceWidget(self.init_widget,pain_widget)
        self.init_widget.deleteLater()
        self.init_widget = pain_widget

    @pyqtSlot()
    def pump_apply_pain(self):
        wait_widget = QWidget()
        wait_layout = QVBoxLayout()
        wait_label = QLabel("Vänta")
        wait_label.setAlignment(Qt.AlignCenter)
        wait_label.setStyleSheet(self.big_label_stylesheet)
        wait_layout.addWidget(wait_label)
        wait_widget.setLayout(wait_layout)
        self.main_layout.replaceWidget(self.init_widget,wait_widget)
        self.init_widget.deleteLater()
        self.init_widget = wait_widget

        self.apply_pain = False

        # # calculate threshold values
        # pain_from_pump = mean(self.thresholds)
        # # increment by 10%
        # pain = pain_from_pump + pain_from_pump*0.1
        # pain_mmHg = round(float(pain)*1.01372549,2)
        # # get pressure by subtracting 50%
        # pressure = pain_from_pump - pain_from_pump*0.5
        # print(round(pain))
        # print(round(pressure))
        # write thresholds to main log file
        # f = open(self.log_path, "a")
        # f.write("\nPain Threshold:    "+str(round(pain))+"\n")
        # f.write("Pain Threshold:    "+str(pain_mmHg)+" mmHg\n")
        # f.write("\n\nFormula for pain threshold:    (threshold1+threshold2+threshold3)/3 + ((threshold1+threshold2+threshold3)/3)*0.1")
        # f.write("\nFormula for pain threshold mmHg:    pain threshold*"+str(1.01372549))
        # # f.write("Pressure Threshold:    "+str(round(pressure))+"\n")
        # f.close()

        # bytes read from pump
        # self.pumpBytes = bytearray([])
        # # initialize serial      
        # if not serial.Serial(self.com_port, BAUDRATE, timeout = 0.5).is_open:   
        #     print("Port was closed")                           
        #     self.pumpController = serial.Serial(self.com_port, BAUDRATE, timeout = 0.5) 
        # else:
        #     print("Port was already opened") 
        #     serial.Serial(self.com_port, BAUDRATE, timeout = 0.5).close()  
        #     self.pumpController = serial.Serial(self.com_port, BAUDRATE, timeout = 0.5) 
        #         
        # # This is the rate of inflation and speed of the motor. 
        # # It progresses stepwise where this value indicates 
        # # how many seconds it remains on this step before accelerating again. 
        # # Value is in seconds. This is required for the motor to be able to handle 
        # # the pressure inside the system, otherwise it would slow down to a halt.                                 
        # outputLevel = 1                                                 
        # # prepare the start and stop bytes
        # start_command_list = [ord('S'), COMMAND_START_CODE, round(pain), outputLevel, 5, 0]
        # # to start the pump
        # # send one command at a time with a delay in order for the pump not to miss anything
        # for i in range(len(start_command_list)):
        #     self.pumpController.write(bytearray([start_command_list[i]]))
        #     time.sleep(0.02)
        # # log time when pump starts sending data
        # self.send_pump_start_command_time = datetime.datetime.now()
        self.send_pump_start_command_time = datetime.datetime.now()
        # wait a bit before next pumping
        PyQt5.QtCore.QTimer.singleShot(5000, self.the_end)

    def the_end(self):
        tack_widget = QWidget()
        tack_layout = QVBoxLayout()
        tack_label = QLabel("Tack")
        tack_label.setAlignment(Qt.AlignCenter)
        tack_label.setStyleSheet(self.big_label_stylesheet)
        tack_layout.addWidget(tack_label)
        tack_widget.setLayout(tack_layout)
        self.main_layout.replaceWidget(self.init_widget,tack_widget)
        self.init_widget.deleteLater()
        self.init_widget = tack_widget

        #################################
        # WRITE PUMP DATA TO A FILE
        # read all data that was sent by the pump
        # pump_data= self.pumpController.read(size=self.pumpController.in_waiting)
        # if len(pump_data) > 0:
        #     self.pumpBytes += bytearray(pump_data)
        #     # what the bytes look like unmodified 
        #     self.pumpBytes = struct.unpack( "=" + "B" * len(self.pumpBytes), self.pumpBytes)

        # previous_t = self.send_pump_start_command_time   
        # if len(self.pumpBytes) != 0:   
        #     # create files for pump data
        #     self.pump_data_file_name = self.log_file_name.split(".")[0]+"_pumpPain.txt"
        #     pump_data_dump = open(os.path.join(self.dump_path,self.pump_data_file_name),"w")
        #     self.pump_Hg_data_file_name = self.log_file_name.split(".")[0]+"_pumpHgPain.txt"
        #     pump_Hg_data_dump = open(os.path.join(self.dump_path,self.pump_Hg_data_file_name),"w")
        #     for i in range(0,len(self.pumpBytes)):
        #         previous_t_text = previous_t.strftime("%Y-%m-%d %H:%M:%S.%f")
        #         row_pump_data = previous_t_text + "    " + str(self.pumpBytes[i]) + "\n"
        #         pump_data_dump.write(row_pump_data)
        #         row_pump_dataHg =  previous_t_text + "    " + str(float(self.pumpBytes[i])*1.01372549) + "\n"
        #         pump_Hg_data_dump.write(row_pump_dataHg)
        #         # pump sends value every 100ms, therefore samples should be 100ms apart
        #         tt = previous_t + datetime.timedelta(milliseconds=SAMPLE_RATE_MS)
        #         previous_t = tt
        #     pump_data_dump.close()
        #     pump_Hg_data_dump.close()
        # else:
        #     # print("No valid data found :(") 
        #     pass
        # # close serial connection
        # self.pumpController.close()
#                                                              #
# EXECUTE GUI FROM MAIN                                        #
#                                                              #
################################################################
if __name__ == "__main__":
    # Always start by initializing Qt (only once per application)
    app = QApplication([])
    main_widget = MySettingsWidget()
    main_widget.show()
    app.exec_()
   

    print('Done')