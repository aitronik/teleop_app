from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.dropdown import DropDown
from threading import Thread
from kivy.uix.checkbox import CheckBox
from kivy.storage.jsonstore import JsonStore



class StartingScreen(Screen):

    def __init__(self,**kwargs):
        self.connectionHandler = kwargs.get('connectionHandler',None)
        self.screenManager = kwargs.get('screenManager',None)
        self.name = kwargs.get('label_info','StartingScreen')
        super(StartingScreen,self).__init__()
        self.devicebutton = self.ids.devices
        self.devicebutton.bind(on_press=self.drop_down)
        self.dropdown = DropDown()
        self.addBool = True
       

        if self.connectionHandler is None:
            print("Error - You need a Connection Handler")


        self.nearby_devices = self.connectionHandler.getNearbyDevices()
        print('enumerating devices....')

        self.ids.filter_list_checkbox.bind(active=self.on_click_checkbox)
        self.ids.add_list_checkbox.bind(active=self.on_check_add)

        isActive = self.ids.filter_list_checkbox.active
        self.addActive = self.ids.add_list_checkbox.active
        self.on_click_checkbox( self.ids.filter_list_checkbox, isActive)


    def on_check_add(self, instance, value):
        if value is True:
            print("on_add_filtered_list enabled")
            self.addBool = True
        else:
            print("on_add_filtered_list disabled")
            self.addBool = False

    def on_add_filtered_list(self, instance, device_name):
        print("[StartingScreen] on_add_filtered_list")
        store = JsonStore("devices_list.json")
        if store.exists(device_name) is not True:
            print("Adding new device to the .json file...")
            store.put(device_name, name=device_name)
        
    def on_click_checkbox(self, instance, value): 
        self.dropdown.clear_widgets()       
        if(len(self.nearby_devices)>0):

            print(len(self.nearby_devices))
            k = 0
            list,ids_devices = self.connectionHandler.filter_list(self.nearby_devices,value)  

            for bdname in list:
                btn = Button(text=bdname, size_hint_y=None, height=100)
 
                btn.id= str(ids_devices[k])
                btn.bind(on_release=lambda btn: self.dropdown.select(btn.text))
                btn.bind(on_press=self.connect_device)

                self.dropdown.add_widget(btn)
                k = k+1
        else:
            print('no devices')
            self.ids.label_info.text = "There are no paired devices. Add them manually"
 
    def on_enter(self):
        self.connectionHandler.setCurrentScreen(self)
        self.connectionHandler.initConnection()
        self.devicebutton.text = " Devices list"

    def drop_down(self, devicebutton):
        self.devicebutton.bind(on_release=self.dropdown.open)
        self.dropdown.bind(on_select=lambda instance, x: setattr(devicebutton, 'text', x))

    def connect_device(self,btn):
        print("Button Pressed")
        if self.addBool is False:
            print("Device name won't be saved.")
        else:
            self.on_add_filtered_list( self.ids.add_list_checkbox, btn.text)
        self.screenManager.device_id = int(btn.id)
        self.goToChannelScreen()
        
    def goToChannelScreen(self): 
        print("goToChannelScreen")
        self.screenManager.current = 'ChannelScreen'
        self.screenManager.transition.direction = 'left'

    def goToStartingScreen(self): 
        print("goToStartingScreen")
        self.screenManager.current = 'StartingScreen'
        self.screenManager.transition.direction = 'left'

    def goToTeleopScreen(self): 
        print("goToTeleopScreen")
        self.screenManager.current = 'TeleOpScreen'
        self.screenManager.transition.direction = 'left'
       