import time
from kivy.uix.screenmanager import Screen
from kivy.clock import Clock
from joystick.joystick import Joystick
from kivy.graphics import Color
from plyer import gps
from plyer import spatialorientation
from jnius import autoclass
from kivy.properties import(BooleanProperty, NumericProperty,
                            ListProperty, ReferenceListProperty)


VEHICLE_OMNI = 0
VEHICLE_DIFF = 1

class JoyStickScreen(Screen):

    def __init__(self, **kwargs):
        self.GPS_BOOL = 0
        self.firstCall = 1
        self.joyStatus = 0
        self.gps = gps
        self.compass = spatialorientation
        self.connectionHandler = kwargs.get('connectionHandler',None)
        self.screenManager = kwargs.get('screenManager',None)
        self.name = kwargs.get('label_info','JoyStickScreen')
        super(JoyStickScreen,self).__init__()
        self.ids.bool.bind(on_press=self.on_vehicle_type_change)
        self.ids.joy.bind(pad=self.update_coordinates)
        self.ids.follow_status.bind(on_press=self.on_follow_me)
        self.ids.joy.bind(on_touch_up=self.on_joy_touch_up)
        self.ids.back.bind(on_press=self.on_disconnect_device)
        

    def on_follow_me(self, button):
        if self.GPS_BOOL is 0:
            self.GPS_BOOL = 1
            button.text = "GPS is ON"
            self.gps.start(1000,0)
            self.compass.enable_listener()
            Clock.schedule_interval(self.update_orientation, 1.0/10)
        else:
            self.GPS_BOOL = 0
            button.text = "GPS is OFF"
            self.gps.stop()
            self.compass.disable_listener()
            Clock.unschedule(self.update_orientation, all=True)
        
        self.connectionHandler.sendState(self.GPS_BOOL,self.joyStatus)

    def on_vehicle_type_change(self, button):
        if self.connectionHandler.vehicle_type == VEHICLE_DIFF:
            self.connectionHandler.vehicle_type = VEHICLE_OMNI
            self.ids.id_label_name.text = "Vehicle Type: Omnidirectional"
        else:
            self.connectionHandler.vehicle_type = VEHICLE_DIFF
            self.ids.id_label_name.text = "Vehicle Type: Differential"

    def on_joy_touch_up(self, val, touch):
        if val._touch_is_active(touch) and not(val.sticky):
            val.center_pad()
            self.joyStatus = 0
            self.firstCall = 1
            self.connectionHandler.stop_speed()
            self.connectionHandler.sendState(self.GPS_BOOL,self.joyStatus)
            return True

        return super(Joystick, val).on_touch_up(touch)

    def update_coordinates(self, joystick, pad):
        if(self.firstCall is 1):
            self.firstCall = 0
            self.joyStatus = 1
            self.connectionHandler.sendState(self.GPS_BOOL,self.joyStatus)
        self.connectionHandler.update_coordinates(pad[0],pad[1])   

    def update_orientation(self, dt):
        if self.compass.orientation[0] is not None and self.compass.orientation[1] is not None and self.compass.orientation[2] is not None:
            azimuth = self.compass.orientation[0]
            pitch = self.compass.orientation[1]
            roll = self.compass.orientation[2]
            self.connectionHandler.update_orientation(azimuth,pitch,roll)        

    def on_enter(self):
        print("JoyStickScreen enter")
        if self.connectionHandler.vehicle_type == VEHICLE_DIFF:
            self.ids.id_label_name.text = "Vehicle Type: Differential"
        else:
            self.ids.id_label_name.text = "Vehicle Type: Omnidirectional"
        self.connectionHandler.setCurrentScreen(self)
        self.connectionHandler.setTeleopMode()

        self.GPS_BOOL = self.connectionHandler.gpsIsOn # get common gps status
        if self.GPS_BOOL == 1:
            self.ids.follow_status.text = 'GPS is ON'
        else:
            self.ids.follow_status.text = 'GPS is OFF'
        self.ids.id_dev_label_name.text = "Device ID: " + str(self.connectionHandler.devId)

    def on_leave(self):
        self.connectionHandler.stop_speed()
        self.ids.joy.center_pad()
        self.on_check_flag()
        
    def on_disconnect_device(self, back):
        self.on_check_flag(disconnection=True)
        self.connectionHandler.stop_speed()
        self.connectionHandler.sendState(self.GPS_BOOL,self.joyStatus)
        self.connectionHandler.disconnect_device()
        self.connectionHandler.disconnect()
        self.goToStartingScreen()

    def goToTeleopScreen(self): 
        print("goToTeleopScreen")
        self.screenManager.current = 'TeleOpScreen'
        self.screenManager.transition.direction = 'left'       
       
    def goToStartingScreen(self): 
        print("goToStartingScreen")
        self.screenManager.current = 'StartingScreen'
        self.screenManager.transition.direction = 'left'

    def on_check_flag(self, disconnection = False):
        if disconnection == True:
            self.GPS_BOOL = 0
        self.connectionHandler.gpsIsOn = self.GPS_BOOL
        
