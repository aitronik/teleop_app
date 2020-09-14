from .WrappedLabel import WrappedLabel

from kivy.uix.button import Button
from kivy.uix.popup import Popup
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.app import App


from kivy.uix.scrollview import ScrollView
from kivy.properties import StringProperty
from kivy.lang import Builder

long_text = 'yay moo cow foo bar moo baa ' * 100

Builder.load_string('''
<ScrollableLabel>:
    Label:
        size_hint_y: None
        height: self.texture_size[1]
        text_size: self.width, None
        text: root.text
''')


class ScrollableLabel(ScrollView):
    text = StringProperty('')

class ShowErrorApp(App):
    def __init__(self, **kwargs):
        self.label_info = kwargs.get('label_info','Error')
        super(ShowErrorApp,self).__init__()

    def build(self):
        sm2 = ScreenManager()

        box = BoxLayout(orientation = 'vertical', padding = (50))      

        label2 = ScrollableLabel(text=self.label_info)
         
        box.add_widget(label2)
        button = Button(text = "Close", size_hint_y= None, height=200,on_press=quit)
        box.add_widget(button)
        popup = Popup(title='Caught Exception - Error', content=box) 
    
        screen = Screen()
        screen.name ="errorScreen"
        screen.label = label2
        screen.add_widget(popup)
        sm2.screen_error = screen
        sm2.add_widget(screen)
        return sm2
