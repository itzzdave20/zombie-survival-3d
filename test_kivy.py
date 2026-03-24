from kivy.app import App
from kivy.core.window import Window

app = App()
try:
    print(dir(Window._system_keyboard))
except Exception as e:
    print(f"Error: {e}")
