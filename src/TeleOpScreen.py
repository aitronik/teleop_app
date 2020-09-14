from kivy.uix.screenmanager import Screen
from kivy.clock import Clock
from joystick.joystick import Joystick
from kivy.graphics import Color
from kivy.properties import(BooleanProperty, NumericProperty,
                            ListProperty, ReferenceListProperty)

from plyer import accelerometer
from plyer import gps
from plyer import spatialorientation
from jnius import autoclass

import time

VEHICLE_OMNI = 0
VEHICLE_DIFF = 1

class TeleOpScreen(Screen):

    def __init__(self, **kwargs):
        self.gps = gps
        self.compass = spatialorientation
        self.accOn = 0
        self.GPS_BOOL = 0
        self.connectionHandler = kwargs.get('connectionHandler',None)
        self.screenManager = kwargs.get('screenManager',None)
        self.name = kwargs.get('label_info','TeleOpScreen')
        super(TeleOpScreen,self).__init__()
        self.ids.bool.bind(on_press=self.on_vehicle_type_change)
        self.ids.button_info_touch.bind(on_press=self.on_enableAcc)
        self.ids.back.bind(on_press=self.on_disconnect_device)
        self.ids.follow_status.bind(on_press=self.on_follow_me)
        self.gps.configure(on_location = self.update_gps_coordinates, on_status = None)
        
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

        self.connectionHandler.sendState(self.GPS_BOOL,self.accOn)
    
    def update_gps_coordinates(self, **kwargs):
        for k, v in kwargs.items():
            if k is 'lat':
                lat = v
            if k is 'lon':
                lon = v

        self.connectionHandler.update_gps(lat, lon)

    def update_orientation(self, dt):
        if self.compass.orientation[0] is not None and self.compass.orientation[1] is not None and self.compass.orientation[2] is not None:
            azimuth = self.compass.orientation[0]
            pitch = self.compass.orientation[1]
            roll = self.compass.orientation[2]
            self.connectionHandler.update_orientation(azimuth,pitch,roll)

    def on_status(self, stype, status):
        print("GPS status: ", stype, " ", status)

    def on_enableAcc(self, button):
        if self.accOn is 0:
            button.text = 'Drive'
            accelerometer.enable()
            Clock.schedule_interval(self.update_tele_coordinates, 1.0/10)
            self.accOn = 1
        else:
            button.text = 'Stand by'
            self.connectionHandler.stop_speed()
            self.stop_clock()

        self.connectionHandler.sendState(self.GPS_BOOL,self.accOn)

    def on_vehicle_type_change(self, button):
        if self.connectionHandler.vehicle_type == VEHICLE_DIFF:
            self.connectionHandler.vehicle_type = VEHICLE_OMNI
            self.ids.id_label_name.text = "Vehicle Type: Omnidirectional"
        else:
            self.connectionHandler.vehicle_type = VEHICLE_DIFF
            self.ids.id_label_name.text = "Vehicle Type: Differential"

    def update_tele_coordinates(self, dt):
        if accelerometer.acceleration[0] is not None and accelerometer.acceleration[1] is not None:
            y = -(accelerometer.acceleration[1]/9.81)
            x = -(accelerometer.acceleration[0]/9.81)
            self.connectionHandler.update_coordinates(x,y)           

    def on_enter(self):
        self.connectionHandler.setCurrentScreen(self)
        self.connectionHandler.setTeleopMode()

        if self.connectionHandler.vehicle_type == VEHICLE_DIFF:
            self.ids.id_label_name.text = "Vehicle Type: Differential"
        else:
            self.ids.id_label_name.text = "Vehicle Type: Omnidirectional"

        self.ids.id_dev_label_name.text = "Device ID: " + str(self.connectionHandler.devId)
        
        self.GPS_BOOL = self.connectionHandler.gpsIsOn # get common gps status
        if self.GPS_BOOL == 1:
            self.ids.follow_status.text = 'GPS is ON'
        else:
            self.ids.follow_status.text = 'GPS is OFF'
        
    def on_check_flags(self, disconnection = False):
        if self.accOn is 1:
            self.stop_clock()
        if disconnection is True:
            self.GPS_BOOL = 0
        self.connectionHandler.gpsIsOn = self.GPS_BOOL

    def on_leave(self):
        self.connectionHandler.stop_speed()
        self.ids.button_info_touch.text = 'Stand by'
        self.on_check_flags()        

    def on_disconnect_device(self, back):
        self.ids.button_info_touch.text = 'Stand by'
        self.connectionHandler.stop_speed()
        self.on_check_flags(disconnection=True)
        self.connectionHandler.sendState(self.GPS_BOOL,self.accOn)
        self.connectionHandler.disconnect_device()
        self.connectionHandler.disconnect()
        self.goToStartingScreen()

    def goToTeleopScreen(self): 
        self.screenManager.current = 'TeleOpScreen'
        self.screenManager.transition.direction = 'left'

    def goToStartingScreen(self): 
        self.screenManager.current = 'StartingScreen'
        self.screenManager.transition.direction = 'left'

    def stop_clock(self):
        Clock.unschedule(self.update_tele_coordinates, all=True)
        accelerometer.disable()
        self.accOn = 0       
