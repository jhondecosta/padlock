import traceback

try:
    from padlock import NetPadlockAndroidApp
    NetPadlockAndroidApp().run()
except Exception:
    err = traceback.format_exc()
    from kivy.app import App
    from kivy.uix.scrollview import ScrollView
    from kivy.uix.label import Label

    class ErrorApp(App):
        def build(self):
            sv = ScrollView()
            lbl = Label(text=err, size_hint_y=None, halign="left", valign="top")
            lbl.bind(texture_size=lambda inst, val: setattr(inst, "height", val[1]))
            lbl.bind(width=lambda inst, val: setattr(inst, "text_size", (val, None)))
            sv.add_widget(lbl)
            return sv

    ErrorApp().run()
