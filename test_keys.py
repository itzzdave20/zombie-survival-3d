from kivy.app import App
from kivy.core.window import Window
from kivy.uix.widget import Widget

class TestWidget(Widget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        Window.bind(on_key_down=self.on_key_down)
    
    def on_key_down(self, window, key, scancode, codepoint, modifier):
        print(f"key={key}, scancode={scancode}, codepoint={codepoint}, modifier={modifier}")
        print(f"type(key)={type(key)}, type(scancode)={type(scancode)}")

class TestApp(App):
    def build(self):
        return TestWidget()

TestApp().run()
