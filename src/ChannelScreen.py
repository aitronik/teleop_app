from kivy.uix.screenmanager import Screen
from kivy.uix.button import Button
from kivy.uix.dropdown import DropDown

class ChannelScreen(Screen):

    def __init__(self,**kwargs):
        self.connectionHandler = kwargs.get('connectionHandler',None)
        self.screenManager = kwargs.get('screenManager',None)
        self.name = kwargs.get('channel_info','ChannelScreen')
        super(ChannelScreen,self).__init__()
        self.channelbutton = self.ids.channels
        self.backbutton = self.ids.back
        self.backbutton.bind(on_press = self.goBack)
        self.channelbutton.bind(on_press = self.drop_down_ch)
        self.dropdown = DropDown()

    def on_enter(self):
        self.channelbutton.text = "Channels"
        self.dropdown.clear_widgets()       
        for index in range(5):
            btn = Button(text='%d' % int(index+1), size_hint_y=None, height=100)
            btn.id= str(index+1)
            btn.bind(on_release=lambda btn: self.dropdown.select(btn.text))
            btn.bind(on_press=self.connect_device)
            self.dropdown.add_widget(btn)

    def drop_down_ch(self, channelbutton):
        self.channelbutton.bind(on_release=self.dropdown.open)
        self.dropdown.bind(on_select=lambda instance, x: setattr(channelbutton, 'text', x))

    def connect_device(self,btn):
        self.connectionHandler.connectDevice(self.screenManager.device_id,int(btn.id))

    def goToChannelScreen(self): 
        print("goToChannelScreen")
        self.screenManager.current = 'ChannelScreen'
        self.screenManager.transition.direction = 'left'

    def goBack(self, button):
        self.goToStartingScreen()        
        
    def goToTeleopScreen(self): 
        print("goToTeleopScreen")
        self.screenManager.current = 'TeleOpScreen'
        self.screenManager.transition.direction = 'left'

    def goToStartingScreen(self): 
        print("goToStartingScreen")
        self.screenManager.current = 'StartingScreen'
        self.screenManager.transition.direction = 'left'
