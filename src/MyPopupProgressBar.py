from kivy.uix.progressbar import ProgressBar
from kivy.clock import Clock
from kivy.uix.popup import Popup
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.properties import ObjectProperty
from kivy.uix.widget import Widget

class MyPopupProgressBar(Widget):

    progress_bar = ObjectProperty() # Kivy properties classes are used when you create an EventDispatcher.
    
    def __init__(self, **kwa):
        super(MyPopupProgressBar, self).__init__(**kwa) #super combines and initializes two widgets Popup and ProgressBar
        
        self.progress_bar = ProgressBar() # instance of ProgressBar created. 
        self.box = BoxLayout(orientation = 'vertical', padding = (50))
        
        self.button = Button(text = "Close")
        self.button.opacity = 0
        self.button.size_hint_y = 0.2
        self.progress_bar.value = 0
        self.max_progress_bar_value = 100
        # visible= False
        self.box.add_widget(self.progress_bar)
        self.box.add_widget(self.button)
       
        # progress bar assigned to popup
        self.popup = Popup(title='Trying to connect.....', content=self.box) 
        # Binds super widget to on_open.
        self.popup.bind(on_open=self.puopen)
        # Uses clock to call progress_bar_start() (callback) one time only
        Clock.schedule_once(self.progress_bar_start) 


    def progress_bar_start(self, instance): # Provides initial value of of progress bar and lanches popup
        self.progress_bar.value = 1 # Initial value of progress_bar
        self.popup.open() # starts puopen()

    def next(self, dt): # Updates Project Bar
        if self.progress_bar.value >= self.max_progress_bar_value: # Checks to see if progress_bar.value has met 100
            return False # Returning False schedule is canceled and won't repeat
        self.progress_bar.value += 1 # Updates progress_bar's progress

    def puopen(self, instance): # Called from bind.
        Clock.schedule_interval(self.next, .15) # Creates Clock event scheduling next() every 5-1000th of a second.
    
    def success(self):
        self.popup.title = "Success"
        self.progress_bar.value = self.max_progress_bar_value
        self.button.opacity = 1
        self.button.bind(on_press=self.popup.dismiss)
        self.popup.dismiss()
      
    def notSuccess(self):
        self.popup.title = "Unable to connect to this Device"
        self.progress_bar.value = self.max_progress_bar_value        
        self.button.opacity = 1
        self.button.bind(on_press=self.popup.dismiss)

        