from .ui_about_dialog import Ui_dlgAbout

from PyQt5 import QtCore, QtGui, QtWidgets
from .ui_about_dialog import Ui_dlgAbout

class AboutDialog(QtWidgets.QDialog, Ui_dlgAbout):
    def __init__(self):
        QtWidgets.QDialog.__init__(self)
        # Set up the user interface from Designer.
        # After setupUI you can access any designer object by doing
        # self.<objectname>, and you can use autoconnect slots - see
        # http://qt-project.org/doc/qt-4.8/designer-using-a-ui-file.html
        # #widgets-and-dialogs-with-auto-connect
        self.setupUi(self)
