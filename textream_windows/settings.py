from PyQt6.QtCore import QSettings

class AppSettings:
    def __init__(self):
        self.settings = QSettings("Textream", "TextreamWindows")

    @property
    def line_count(self):
        return int(self.settings.value("line_count", 3))

    @line_count.setter
    def line_count(self, value):
        self.settings.setValue("line_count", value)

    @property
    def waveform_color(self):
        return self.settings.value("waveform_color", "#FFC832")

    @waveform_color.setter
    def waveform_color(self, value):
        self.settings.setValue("waveform_color", value)

    @property
    def waveform_style(self):
        return self.settings.value("waveform_style", "bars") # bars, dots, wave

    @waveform_style.setter
    def waveform_style(self, value):
        self.settings.setValue("waveform_style", value)
        
    @property
    def theme(self):
        return self.settings.value("theme", "dark") # dark, light

    @theme.setter
    def theme(self, value):
        self.settings.setValue("theme", value)

    @property
    def text_color(self):
        return self.settings.value("text_color", "#FFFFFF")

    @text_color.setter
    def text_color(self, value):
        self.settings.setValue("text_color", value)

    @property
    def highlight_color(self):
        return self.settings.value("highlight_color", "#FFC832") # Matching default waveform gold

    @highlight_color.setter
    def highlight_color(self, value):
        self.settings.setValue("highlight_color", value)

    @property
    def font_family(self):
        return self.settings.value("font_family", "Segoe UI")

    @font_family.setter
    def font_family(self, value):
        self.settings.setValue("font_family", value)

    @property
    def font_size(self):
        return int(self.settings.value("font_size", 24))

    @font_size.setter
    def font_size(self, value):
        self.settings.setValue("font_size", value)

    def reset(self):
        self.settings.clear()

settings = AppSettings()
