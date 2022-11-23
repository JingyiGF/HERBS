from PyQt5.QtWidgets import *


class AboutHERBSWindow(QMessageBox):
    def __init__(self):
        super().__init__()

        self.setIcon(QMessageBox.NoIcon)
        self.setWindowTitle("About HERBS")
        self.setText("HERBS is aiming to provide a pleasant platform "
                     "for histological image registration in neuroscience. \n"
                     "\n"
                     "If you have any requests or questions ---- \n"
                     "\n"
                     "Please contact maintainers: \n"
                     "jingyi.g.fuglstad@gmail.com \n"
                     "\n"
                     "Or leave an issue/discussion on HERBS GitHub: \n"
                     "https://github.com/JingyiGF/HERBS \n"
                     "\n"
                     "Please always read the Update Log after updating: \n"
                     "https://github.com/JingyiGF/HERBS/blob/main/UpdateLog.md")
        self.setStandardButtons(QMessageBox.Close)
