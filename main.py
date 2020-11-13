from PyQt5 import uic
from PyQt5.QtWidgets import (QAction, QApplication, QFileDialog, QMainWindow, QLineEdit,
            QProgressBar, QMessageBox, QHBoxLayout, QVBoxLayout, QWidget, QLabel,
            QMessageBox, QToolButton, QComboBox, QErrorMessage, qApp, QToolBar,
            QStatusBar, QSystemTrayIcon, QMenu)
from PyQt5.QtCore import (QFile, QPoint, QRect, QSize, Qt,
            QProcess, QThread, pyqtSignal, pyqtSlot, Q_ARG , Qt, QMetaObject, QObject)
from PyQt5.QtGui import QIcon, QFont, QClipboard, QPixmap, QImage
from easysettings import EasySettings
import sys, os, winreg, time, schedule
from win10toast import ToastNotifier
#icon taskbar
try:
    from PyQt5.QtWinExtras import QtWin
    myappid = 'darkmode.python.scheudule.program'
    QtWin.setCurrentProcessExplicitAppUserModelID(myappid)    
except ImportError:
    pass
#pyinstaller
def resource_path(relative_path):
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath('.'), relative_path)
# variables
dmon_icon = resource_path("./icons/dm_on.png") #darkode on
dmoff_icon = resource_path("./icons/dm_off.png") #darkmode off
dmon_ico = resource_path("./icons/dm_on.ico") #darkode on
dmoff_ico = resource_path("./icons/dm_off.ico") #darkmode off
settings_icon = resource_path("./icons/settings.png")
config_gui = resource_path("./gui/config.ui")
config = EasySettings("./config/config.conf")
dm_cfg = resource_path("./icons/dm_cfg.png") #no settings proviced
#App
app = QApplication([])
app.setQuitOnLastWindowClosed(False)
toaster = ToastNotifier()

#config window
class Config(QWidget):
    def __init__(self):
        super().__init__()
        UIFile = QFile(resource_path(config_gui))
        UIFile.open(QFile.ReadOnly)
        uic.loadUi(UIFile, self)
        UIFile.close()

c = Config()

#change winreg
REG_PATH = r'SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Themes\\Personalize'
def set_reg(name, value):
    try:
        winreg.CreateKey(winreg.HKEY_CURRENT_USER, REG_PATH)
        registry_key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, REG_PATH, 0, 
                                       winreg.KEY_WRITE)
        winreg.SetValueEx(registry_key, name, 0, winreg.REG_SZ, value)
        winreg.CloseKey(registry_key)
        return True
    except WindowsError:
        return False

            
# Create the icon
icon = QIcon(resource_path(dm_cfg))

# Create the tray
tray = QSystemTrayIcon()
tray.setIcon(icon)
tray.setVisible(True)


#sets darkmode on and changes icon
def cmd_dmon():
    on_icon = QIcon(resource_path(dmon_icon))
    tray.setIcon(on_icon)
    set_reg('AppsUseLightTheme', str(0))
    set_reg('SystemUsesLightTheme', str(0))
    toaster.show_toast("Darkmode",
                   "Welcome to the dark side!",
                   icon_path=dmon_ico,
                   duration=5,
                   threaded=True)
    while toaster.notification_active(): time.sleep(0.1)
    

#sets darkmode off and changes icon
def cmd_dmoff():
    off_icon = QIcon(resource_path(dmoff_icon))
    tray.setIcon(off_icon)
    set_reg('AppsUseLightTheme', str(1))
    set_reg('SystemUsesLightTheme', str(1))
    toaster.show_toast("Darkmode",
                   "Welcome to the light side!",
                   icon_path=dmoff_ico,
                   duration=5,
                   threaded=True)
    while toaster.notification_active(): time.sleep(0.1)

def cmd_config():
    c.show()
    c.setWindowIcon(QIcon(settings_icon))

#darkmode on
menu = QMenu()
dm_on = QAction("Darkmode On")
menu.addAction(dm_on)
dm_on.triggered.connect(cmd_dmon)
#darkmode off

dm_off = QAction("Darkmode Off")
menu.addAction(dm_off)
dm_off.triggered.connect(cmd_dmoff)
# Settings

configw = QAction("Settings")
menu.addAction(configw)
configw.triggered.connect(cmd_config)

# Quit app
dmquit = QAction("Quit")
dmquit.triggered.connect(app.quit)
menu.addAction(dmquit)

# Add the menu to the tray
tray.setContextMenu(menu)
tray.setToolTip("Darkmode")


app.exec_()
