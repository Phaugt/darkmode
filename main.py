from PyQt5 import uic
from PyQt5.QtWidgets import (QAction, QApplication, QFileDialog, QMainWindow, QLineEdit,
            QProgressBar, QMessageBox, QHBoxLayout, QVBoxLayout, QWidget, QLabel,
            QMessageBox, QToolButton, QComboBox, QErrorMessage, qApp, QToolBar,
            QStatusBar, QSystemTrayIcon, QMenu, QTimeEdit)
from PyQt5.QtCore import (QFile, QPoint, QRect, QSize, Qt,
            QProcess, QThread, pyqtSignal, pyqtSlot, Q_ARG , Qt, QMetaObject, QObject)
from PyQt5.QtGui import QIcon, QFont, QClipboard, QPixmap, QImage
from easysettings import EasySettings, esGetError, esError, esSaveError, esSetError
import sys, os, winreg, time, schedule, greet, threading
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
settings_ico = resource_path("./icons/settings.ico")
config_gui = resource_path("./gui/config.ui")
config = EasySettings("./config/config.conf")
dm_cfg = resource_path("./icons/dm_cfg.png") #no settings proviced
REG_PATH = r'SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Themes\\Personalize' #values changed for windows theme
#EDGE_PATH = r'SOFTWARE\\Classes\\Local Settings\\Software\\Microsoft\\Windows\\CurrentVersion\\AppContainer\\Storage\\microsoft.microsoftedge_8wekyb3d8bbwe\\MicrosoftEdge\\Main' #old edge not chromium based

#App
app = QApplication([])
app.setQuitOnLastWindowClosed(False)
toaster = ToastNotifier()
# Create the icon
icon = QIcon(resource_path(dm_cfg))

# Create the tray
tray = QSystemTrayIcon()
tray.setIcon(icon)
tray.setVisible(True)
#config window
class Config(QWidget):
    def __init__(self):
        super().__init__()
        UIFile = QFile(resource_path(config_gui))
        UIFile.open(QFile.ReadOnly)
        uic.loadUi(UIFile, self)
        UIFile.close()
        
        #buttons
        self.saveexit.clicked.connect(self.SaveConfigExit)
        self.saveconfig.clicked.connect(self.SaveConfig)
        #self.time_dmon.setTime(config.get('dark_start'))
        
    def SaveConfigExit(self):
        #config.set('username',self.alt_username.text())
        config.set('dark_start',self.time_dmon.time())
        config.set('dark_stop', self.time_dmoff.time())
        config.save()
        c.close()
    def SaveConfig(self):
        #config.set('username',self.alt_username.text())
        config.set('dark_start',self.time_dmon.time())
        config.set('dark_stop', self.time_dmoff.time())
        config.save()


#to call config window
c = Config()
try:    
    if config.get("state")  == "":
        c.setWindowIcon(QIcon(dm_cfg))
    else:
        c.setWindowIcon(QIcon(settings_icon))
except Exception as exEx:
    pass
            


#change winreg
def set_reg(name, value, path, reg_type):
    try:
        winreg.CreateKey(winreg.HKEY_CURRENT_USER, path)
        registry_key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, path, 0, 
                                       winreg.KEY_WRITE)
        winreg.SetValueEx(registry_key, name, 0, reg_type, value)
        winreg.CloseKey(registry_key)
        return True
    except WindowsError:
        return False


#sets darkmode on and changes icon
def cmd_dmon():
    on_icon = QIcon(resource_path(dmon_icon))
    tray.setIcon(on_icon)
    set_reg('AppsUseLightTheme', str(0), REG_PATH, winreg.REG_SZ)
    set_reg('SystemUsesLightTheme', str(0), REG_PATH, winreg.REG_SZ)
    notification(greet.greetdark, dmon_ico)
    #set_reg('Theme', int(0), EDGE_PATH, winreg.REG_DWORD) #old edge not chromium based

    

#sets darkmode off and changes icon
def cmd_dmoff():
    off_icon = QIcon(resource_path(dmoff_icon))
    tray.setIcon(off_icon)
    set_reg('AppsUseLightTheme', str(1), REG_PATH, winreg.REG_SZ)
    set_reg('SystemUsesLightTheme', str(1), REG_PATH, winreg.REG_SZ)
    notification(greet.greetlight, dmoff_ico)
    #set_reg('Theme', int(1), EDGE_PATH, winreg.REG_DWORD) #old edge not chromium based


#calls QWidget
def cmd_config():
    c.show()
    
#toaster
def notification(message, ico):
    toaster.show_toast("Darkmode",
                   message,
                   icon_path=ico,
                   duration=5,
                   threaded=True)
    #while toaster.notification_active(): time.sleep(0.1)

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
