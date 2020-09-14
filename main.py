import kivy
kivy.require('1.11.1')

from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager
from kivy.app import App


from src.StartingScreen import StartingScreen
from src.TeleOpScreen import TeleOpScreen
from src.ShowErrorApp import ShowErrorApp
from src.ConnectionHandler import ConnectionHandler
from src.JoyStickScreen import JoyStickScreen
from src.ChannelScreen import ChannelScreen

import requests
import time
import traceback

Builder.load_string("""

<StartingScreen>:
                
    Label:
        text: 'Please connect to a device from Devices list'
        size_hint_x: 1
        size_hint_y: 1
        id: label_info
        
    GridLayout:
        cols: 6
        size_hint_y: 0.4
   
        CheckBox:
            color: 1, 1, 1 
            id: filter_list_checkbox
            size_hint_x: 0.2
            active: False
       
        Label:
            text: 'Filter devices'
            size_hint_x: 0.3

        Label:
            text: ' '
            size_hint_x: 0.1

        CheckBox:
            color: 1, 1, 1 
            id: add_list_checkbox
            size_hint_x: 0.3 
            active: True
       
        Label:
            text: 'Remember device'
            size_hint_x: 0.3

        Label:
            text: ' '
            size_hint_x: 0.2
            
    Button:
        id: devices
        text: 'Devices List'
        size_hint_y: None
        height: 200


<ChannelScreen>:   
    GridLayout:
        rows: 4
        Button:
            text: 'Back'
            id: back
            size_hint_y: 0.1
        Label:
            text: 'Please select a channel to connect to'
            size_hint_x: 1
            size_hint_y: 1
            id: channel_info
        Button:
            id: channels
            text: 'Channels'
            size_hint_y: None
            height: 200


<TeleOpScreen>:
    BoxLayout:
        orientation: 'vertical'
        GridLayout:
            cols: 3
            size_hint_y: 0.1
            Button:
                text: 'Disconnect'
                id:back
                size_hint_y: None
                on_release:
                    root.manager.current = 'StartingScreen'
                    root.manager.transition.direction = 'right'
            Button:
                text: 'GPS is OFF'
                size_hint_y: None
                id: follow_status
                size_hint_y: None

        BoxLayout:
            orientation: 'vertical'
            size_hint_y: 1
            id: layout_info
            
            canvas:   
                Color:
                    rgba: .5, .5, .5, 1
                Line:
                    width: 2
                    rectangle: self.x, self.y, self.width, self.height       

            Label:
                text: 'Device ID: -'
                size_hint_y: 0.1
                size_hint_x: 1
                height: 70
                id: id_dev_label_name

            Label:
                text: 'Vehicle Type: Differential'
                size_hint_y: 0.1
                size_hint_x: 1.0
                height: 70
                id: id_label_name
                  
            BoxLayout:
                orientation: 'vertical'
                size_hint_y: 1
                
                Button:
                    id: button_info_touch
                    text: 'Stand by'
                    size_hint_y: 0.9
                    size_hint_x: 1

                Label:
                    id: label_info_joy
                    text: 'Move Vehicle'
                    size_hint_y: 0.1    
                    height: 100
                    size_hint_x: 1
        GridLayout:
            cols: 3
            size_hint_y: 0.1
            Button:
                text: 'Switch mode'
                size_hint_y: None
                id: bool
            Button:
                text: 'Joy'
                size_hint_y: None
                on_release:
                    root.manager.current = 'JoyStickScreen'
                    root.manager.transition.direction = 'left'


<JoyStickScreen>:
    BoxLayout:
        orientation: 'vertical'
        GridLayout:
            cols: 3
            size_hint_y: 0.1
            Button:
                text: 'Disconnect'
                id:back
                size_hint_y: None
                on_release:
                    root.manager.current = 'StartingScreen'
                    root.manager.transition.direction = 'right'
            Button:
                text: 'GPS is OFF'
                size_hint_y: None
                id: follow_status
                size_hint_y: None

        BoxLayout:
            orientation: 'vertical'
            size_hint_y: 1
            id: layout_info
            
            canvas:   
                Color:
                    rgba: .5, .5, .5, 1
                Line:
                    width: 2
                    rectangle: self.x, self.y, self.width, self.height
            
            Label:
                text: 'Device ID: -'
                size_hint_y: 0.1
                size_hint_x: 1
                height: 70
                id: id_dev_label_name

            Label:
                text: 'Vehicle Type: Differential'
                size_hint_y: 0.1
                size_hint_x: 1.0
                height: 70
                id: id_label_name
                
            BoxLayout:
                orientation: 'vertical'
                size_hint_y: 1
                
                Joystick:
                    id: joy
                    sticky: False
                    outer_size: 0.8
                    inner_size: 0.6
                    pad_size:   0.375
                    outer_line_width: 0.01
                    inner_line_width: 0.01
                    pad_line_width:   0.01
                    outer_background_color: (0.75, 0.75, 0.75, 0.3)
                    outer_line_color:       (0.25, 0.25, 0.25, 0.3)
                    inner_background_color: (0.75, 0.75, 0.75, 0.1)
                    inner_line_color:       (0.7,  0.7,  0.7,  0.1)
                    pad_background_color:   (0.4,  0.4,  0.4,  0.3)
                    pad_line_color:         (0.35, 0.35, 0.35, 0.3)
                    size_hint_y: 1
                Label:
                    id: label_info_joy
                    text: 'Move Vehicle'
                    size_hint_y: 0.1    
                    height: 100
                    size_hint_x: 1
        GridLayout:
            cols: 3
            size_hint_y: 0.1
            Button:
                text: 'Switch mode'
                size_hint_y: None
                id: bool
            Button:
                text: 'Acc'
                size_hint_y: None
                on_release:
                    root.manager.current = 'TeleOpScreen'
                    root.manager.transition.direction = 'right'

 
""") #UI layout


class TestApp(App):

    def build(self):
        sm = ScreenManager()
        cn = ConnectionHandler()
        to = TeleOpScreen()
        js = JoyStickScreen()
        self.to = to
        self.cn = cn
        self.running = True

        sm.add_widget(StartingScreen(name="StartingScreen",connectionHandler=cn,screenManager=sm))
        sm.add_widget(ChannelScreen(name="ChannelScreen",connectionHandler=cn,screenManager=sm))
        sm.add_widget(TeleOpScreen(name="TeleOpScreen",connectionHandler=cn,screenManager=sm))
        sm.add_widget(JoyStickScreen(name="JoyStickScreen",connectionHandler=cn,screenManager=sm))
        self.request_android_permissions()
        return sm

    def request_android_permissions(self):
        """
        Since API 23, Android requires permission to be requested at runtime.
        This function requests permission and handles the response via a
        callback.
        The request will produce a popup if permissions have not already been
        been granted, otherwise it will do nothing.
        """
        from android.permissions import request_permissions, Permission
        request_permissions([Permission.ACCESS_COARSE_LOCATION, Permission.ACCESS_FINE_LOCATION])

    def on_pause(self):
        print("Pause")
        self.cn.stop_speed()
        time.sleep(0.2)
        # self.to.gps.stop()
        # time.sleep(0.1)
        self.cn.pause()
        return True


    def on_stop(self):
        print("Stop")
        self.cn.stop_speed()
        time.sleep(0.2)
        # self.to.gps.stop()
        # time.sleep(0.1)
        self.cn.pause()


if __name__ == '__main__':
        TestApp().run()
