import time, threading
from threading import Thread, Lock
from kivy.clock import Clock
from kivy.storage.jsonstore import JsonStore
from jnius import PythonJavaClass, java_method
from jnius import autoclass
from jnius import cast
 

import traceback
import struct
import time

BluetoothAdapter = autoclass('android.bluetooth.BluetoothAdapter')
BluetoothDevice = autoclass('android.bluetooth.BluetoothDevice')
BluetoothSocket = autoclass('android.bluetooth.BluetoothSocket')
InputStreamReader = autoclass('java.io.InputStreamReader')
BufferedReader = autoclass('java.io.BufferedReader')
BluetoothHeadset = autoclass('android.bluetooth.BluetoothHeadset')
UUID = autoclass('java.util.UUID')
BufferedReader.size = 128


#TODO MOVE FROM HERE
from .MyPopupProgressBar import MyPopupProgressBar

ID_UPDATE_COORDINATES = 1
ID_HEARTBIT = 2
ID_STOP_SPEED = 3
ID_DISCONNECT = 4
ID_PAUSE = 5
ID_GPS = 6
ID_STATE = 7
ID_ORIENTATION = 8

VEHICLE_OMNI = 0
VEHICLE_DIFF = 1

SUBSTATE_TELEOP = 0
SUBSTATE_UNDEFINED = 1

STATE_IDLE = 0
STATE_INIT = 1
STATE_WAIT_INIT = 2
STATE_RUN = 3
STATE_FAIL = 4
STATE_ABORT = 5
STATE_UNDEFINED = 6


redColor    = [1, 0, 0, 1] # Red
greenColor  = [0, 1, 0, 1] # Green
orangeColor = [1, 0.5, 0, 1]  # Orange
yellowColor = [1, 1, 0, 1] # Yellow
whiteColor   = [1, 1, 1, 1] # White



class ConnectionHandler: 
    def __init__(self, **kwargs):
        print("[ConnectionHandler] __init__")

        self.InitHandler()
        self.InitComm()
        self.state = 0

    def InitHandler(self):
        self.devId = 0
        self.t = None
        self.vehicle_type = VEHICLE_DIFF
        self.current_screen = None
        self.last_screen = None
        self.gpsIsOn = 0        # common gps state


    def InitComm(self):
        self.connected = 0            #stores the status of the conneciton
        self.sock = None              # socket
        self.recv_stream = None       # recv stream
        self.send_stream = None       # send stream
        self.disconnectCounter = 0
        self.mutexWrite = Lock()      #mutex for the send stream
        self.mutexRead = Lock()       #mutex for the read stream


    def setCurrentScreen(self,currentScreen):
        self.last_screen = self.current_screen
        self.current_screen = currentScreen


    def getNearbyDevices(self):
        print("[ConnectionHandler] getNearbyDevices")
        self.nearby_devices = BluetoothAdapter.getDefaultAdapter().getBondedDevices().toArray()
        return self.nearby_devices


    def initConnection(self):
        print("[ConnectionHandler] initConnection")
        self.mutexRead.acquire()
        self.recv_stream = None
        self.mutexRead.release()

        self.mutexWrite.acquire()
        self.send_stream = None
        self.mutexWrite.release()

        self.setTeleopMode()
  

    def connectDevice(self, id, ch):
        print("[ConnectionHandler] connectDevice")
        bdaddr = self.nearby_devices[id]

        if BluetoothAdapter.getProfileConnectionState(BluetoothHeadset.HEADSET) == BluetoothHeadset.STATE_CONNECTED :
            
            string_info = "Connected to a Device : " + bdaddr.getName()
            print(string_info)
        else:
            # string_info = "Please connect to a device from Devices list"
            # print(string_info)
            bdaddr.createBond()
            # print(bdaddr.getBondState())

            if self.connected is 0:
                # bdaddr.createBond()
                self.sock = bdaddr.createRfcommSocket(ch)
                if not self.sock.connected:
                    #ConnectionHandler
                    BluetoothAdapter.cancelDiscovery()
                    # create the thread to invoke other_func with arguments (2, 5)
                    self.t = Thread(target=self.try_connect, args=(2,3))
                    # set daemon to true so the thread dies when app is closed
                    self.t.daemon = True
                    # start the thread
                    self.t.start()
                    self.popup = MyPopupProgressBar()
                    Clock.schedule_interval(self.thread_check, 1.0)

    def thread_check(self, dt):
        if self.popup.progress_bar.value >= self.popup.max_progress_bar_value and self.connected == 0:
            self.disconnect()
            return False

        
    def update_coordinates(self,x,y):
        # print("[ConnectionHandler] update_coordinates")
        BUFFER = bytearray(1)
        BUFFER[0] = ID_UPDATE_COORDINATES
        BUFFER.extend(struct.pack("f", x))
        BUFFER.extend(struct.pack("f", y))
        # print("axis len is :", len(BUFFER))
        self.sendMessage(BUFFER)

    
    def update_orientation(self,azimuth,pitch,roll):
        BUFFER = bytearray(1)
        BUFFER[0] = ID_ORIENTATION
        BUFFER.extend(struct.pack("f", azimuth))
        BUFFER.extend(struct.pack("f", pitch))
        BUFFER.extend(struct.pack("f", roll))
        self.sendMessage(BUFFER)


    def update_gps(self,lat,lon):
        # print("[ConnectionHandler] update_gps")

        BUFFER = bytearray(1)
        BUFFER[0] = ID_GPS
        BUFFER.extend(struct.pack("d", lat))
        BUFFER.extend(struct.pack("d", lon))
        # print("gps len is :", len(BUFFER))
        self.sendMessage(BUFFER)


    def setTeleopMode(self):
        print("[ConnectionHandler] setTeleopMode")
        self.stop_speed()


    def sendState(self,gps,manual):
        self.gpsIsOn = gps #update common gps status 
        BUFFER = bytearray(1)
        BUFFER[0] = ID_STATE
        self.state = 0
        self.state = self.state | manual
        self.state = self.state | (gps << 1)
        # print("CURRENT Status: ", self.state)
        BUFFER.extend(struct.pack("I", self.state))
        self.sendMessage(BUFFER)
        # time.sleep(0.1)

    def sendMessage(self,BUFFER):
        # print("[ConnectionHandler] sendMessage")

        msb = ( len(BUFFER) & 0xFF00 ) >> 8
        lsb = len(BUFFER) & 0x00FF
 
        BUF = bytearray()
        BUF.append(53)
        BUF.append(51)
        BUF.append(msb)
        BUF.append(lsb)
        BUF += BUFFER       
 
        # print(BUF)
        # print(len(BUF))
        ret = False
        if self.connected is 1:

            self.mutexWrite.acquire()
            try:
                self.send_stream.write(BUF)
                self.send_stream.flush()
                self.disconnectCounter = 0
                ret = True
            except:
                self.disconnectCounter +=1
                if (self.disconnectCounter == 3):
                    self.disconnect()

                ret = False

            self.mutexWrite.release()
        
        return ret
        

    def pause(self):
        BUFFER = bytearray(1)
        BUFFER[0] = ID_PAUSE
        self.sendMessage(BUFFER)
        # print("pause sent! ")


    def receiveInfo(self):
        print("[ConnectionHandler] receiveInfo")
        self.mutexRead.acquire()
        
        ret = False
        try:
            bytesread = bytearray(256)
            retval = self.recv_stream.read(bytesread,0,2)
            self.connected = 1
            id = bytesread[0]
            self.devId = id
            
            # bytesread =  bytearray()
            # while( self.bufferedreader.ready()):
            #     byteread = self.bufferedreader.read()
            #     if (byteread < 256):
            #         bytesread += bytes(byteread.to_bytes(1, "big"))
            #     else:
            #         print("..no..",byteread)
            
            # self.invert_axis = True
            ret = True

        except Exception as e:
            print(e)
            ret = False

        self.mutexRead.release()

        return ret


    def receiveStop(self):
        print("[ConnectionHandler] receiveStop")
        self.mutexRead.acquire()
        
        try:

            bytesread = bytearray(256)

            print("available", self.recv_stream.available())
            retval = self.recv_stream.read(bytesread,0,2)
            print("retval, ",retval)
            print("bytes,", bytesread)
            print("type is ", type(bytesread))

            id = bytesread[0]

            print("id",id)

            if id is 13:
                self.current_screen.goToStartingScreen()

        except Exception as e:
            print(e)


    def initialize(self):
        
        ret = self.receiveInfo()

        if ret is True:
            # self.setTeleopMode()
    
            # print("set callback")
            # call my_callback every 0.5 seconds
            threading.Timer(0.5, self.my_heartbit).start()

            # print("go to ..")
            self.current_screen.goToTeleopScreen()
        # else:
            # self.disconnect()
        return ret

    def readMessage(self,lenmsg):
        print("[ConnectionHandler] readMessage")
        message = bytearray()
        counter = 0
        self.mutexRead.acquire()
        while( counter < lenmsg ):
            counter = counter +1
            byteread = self.bufferedreader.read()
            if (byteread > 255):
                break
            else:
                print(byteread)
                message += bytes(byteread.to_bytes(1, "big"))

        self.mutexRead.release()
        # print(message)
        return message

 
    def my_heartbit(self):
        # print("[ConnectionHandler] my_heartbit")    
        
        BUFFER = bytearray(6)
        BUFFER[0] = ID_HEARTBIT
        BUFFER[1] = int(self.vehicle_type)
        ret = self.sendMessage(BUFFER)
     
        if self.connected is 1:
            threading.Timer(0.5, self.my_heartbit).start()
 

    def stop_speed(self):
        print("[ConnectionHandler] stop_speed")
        BUFFER = bytearray(1)
        BUFFER[0] = ID_STOP_SPEED
        BUFFER.extend(struct.pack("f", 0))
        BUFFER.extend(struct.pack("f", 0))
        self.sendMessage(BUFFER)
 

    def disconnect_device(self):
        print("[ConnectionHandler] disconnect_device")
        BUFFER = bytearray(2)
        BUFFER[0] = ID_DISCONNECT
        BUFFER[1] = 1
        self.sendMessage(BUFFER)


    def disconnect(self):
        print("[ConnectionHandler] disconnect")
        self.connected = 0
        self.disconnectCounter = 0
        if self.sock is not None:
            self.sock.close()
            self.sock = None
        self.current_screen.goToStartingScreen()


    def filter_list(self,nearby_devices,isActive):
        print("[ConnectionHandler] filter_list")
        auxList = []
        filteredList = []
        filteredIds = []
        k = 0
        store = JsonStore("devices_list.json")
        for bdaddr in nearby_devices:
            bdname = bdaddr.getName()
            auxList.append(bdname)
            if store.exists(bdname):
                filteredList.append(bdname)
                filteredIds.append(k)
            k = k + 1
        
        if isActive is False:
            filteredList = auxList
            filteredIds = range(len(auxList))       

        return filteredList,filteredIds


    def try_connect(self,a,b):
        print("[ConnectionHandler] separate thread ")
        try:
            self.sock.connect()
            self.connection_established  = True    
            self.connection_init()
            ret = self.initialize()
            if ret is True:
                self.popup.success()
            else:
                self.popup.notSuccess()   
        except:
            global_str = traceback.format_exc()
            print(global_str)
            print("An exception occurred") 
            string_error = " cannot find this device - Devices list"
            self.connection_established  = False
            self.popup.notSuccess()


    def connection_init(self):
        print("[ConnectionHandler] connection_init")
        if self.connection_established is True:
            self.recv_stream = self.sock.getInputStream()

            self.mutexRead.acquire()
            self.bufferedreader = BufferedReader(InputStreamReader(self.recv_stream,"UTF-8"))
            self.mutexRead.release()

            self.mutexWrite.acquire()
            self.send_stream = self.sock.getOutputStream()
            self.mutexWrite.release()

            # self.connected = 1
 
