from PyQt5 import uic
from PyQt5.QtWidgets import (QAction, QApplication, QLineEdit, QMessageBox, QWidget, QLabel,
             QToolButton, QErrorMessage, qApp, QToolBar,
            QStatusBar, QSystemTrayIcon, QMenu, QTimeEdit)
from PyQt5.QtCore import (QFile, QPoint, QRect, QSize, Qt, QTime,
            QProcess, QThread, pyqtSignal, pyqtSlot, Q_ARG , Qt, QMetaObject, QObject)
from PyQt5.QtGui import QIcon, QFont, QClipboard, QPixmap, QImage
from easysettings import EasySettings, esGetError, esError, esSaveError, esSetError
import sys, os, winreg, time, schedule, greet, PyQt5
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
mn_exit = resource_path("./icons/exit.png")
REG_PATH = r'SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Themes\\Personalize' #values changed for windows theme
#EDGE_PATH = r'SOFTWARE\\Classes\\Local Settings\\Software\\Microsoft\\Windows\\CurrentVersion\\AppContainer\\Storage\\microsoft.microsoftedge_8wekyb3d8bbwe\\MicrosoftEdge\\Main' #old edge not chromium based

#App
app = QApplication([])
app.setQuitOnLastWindowClosed(False)
toaster = ToastNotifier()

#toaster
def notification(message, ico):
    toaster.show_toast("Darkmode",
                   message,
                   icon_path=ico,
                   duration=5,
                   threaded=True)
    #while toaster.notification_active(): time.sleep(0.1)

#config window
class Config(QWidget):
    def __init__(self):
        super().__init__()
        UIFile = QFile(resource_path(config_gui))
        UIFile.open(QFile.ReadOnly)
        uic.loadUi(UIFile, self)
        UIFile.close()
        #default times
        try:
            if config.get("first_run") == "Yes":
                on = self.time_dmon.time()
                onh = on.hour()
                onm = on.minute()
                off = self.time_dmoff.time()
                offh = off.hour()
                offm = off.minute()
                config.set("dark_starth",str(onh))
                config.set("dark_startm",str(onm))
                config.set("dark_stoph",str(offh))
                config.set("dark_stopm",str(offm))
                config.set("first_run","No")
                config.set("state","No")
                config.save()
            else:
                onh = config.get("dark_starth")
                onm = config.get("dark_startm")
                offh = config.get("dark_stoph")
                offm = config.get("dark_stopm")
                alt_user = config.get("username")
                on = QTime(int(onh),int(onm))
                off = QTime(int(offh),int(offm))
                self.time_dmon.setTime(on)
                self.time_dmoff.setTime(off)
                self.alt_username.setText(alt_user)
        except Exception:
            notification("Error with Config file", settings_ico)

        #saved config

        #buttons
        self.saveexit.clicked.connect(self.SaveConfigExit)
        self.saveconfig.clicked.connect(self.SaveConfig)
        self.clear.clicked.connect(self.cmd_clear)
        self.alt_username.setToolTip("Requires a restart of Darkmode when changed!")
        #self.time_dmon.setTime(config.get('dark_start'))

    def SaveConfigExit(self):
        try:
            on = self.time_dmon.time()
            onh = on.hour()
            onm = on.minute()
            off = self.time_dmoff.time()
            offh = off.hour()
            offm = off.minute()
            user = self.alt_username.text()
            config.set("dark_starth",str(onh))
            config.set("dark_startm",str(onm))
            config.set("dark_stoph",str(offh))
            config.set("dark_stopm",str(offm))
            config.set("username",str(user))
            config.set("saved_state","yes")
            config.save()
            c.close()
        except Exception:
            notification("Error with Config file", settings_ico)


    def SaveConfig(self):
        on = self.time_dmon.time()
        onh = on.hour()
        onm = on.minute()
        off = self.time_dmoff.time()
        offh = off.hour()
        offm = off.minute()
        user = self.alt_username.text()
        config.set("dark_starth",str(onh))
        config.set("dark_startm",str(onm))
        config.set("dark_stoph",str(offh))
        config.set("dark_stopm",str(offm))
        config.set("username",str(user))
        config.set("saved_state","yes")
        config.save()

    def cmd_clear(self):
        self.time_dmon.setTime(QTime(0,0))
        self.time_dmoff.setTime(QTime(0,0))
        self.alt_username.clear()
#to call config window
c = Config()

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
#check winreg
def get_reg(name, path):
    state = 0
    try:
        registry_key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, path, 0,
                                       winreg.KEY_READ)
        state, regtype = winreg.QueryValueEx(registry_key, name)
        winreg.CloseKey(registry_key)
        return state
    except WindowsError:
        return None

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
    c.setWindowIcon(QIcon(settings_icon))

# Create the tray
tray = QSystemTrayIcon()
try:
    saved_settings = config.get("saved_state")
    if saved_settings == "No":
        icon = QIcon(resource_path(dm_cfg))
        tray.setIcon(icon)
        tray.setToolTip("Darkmode - go to settings!")
    elif get_reg('SystemUsesLightTheme', REG_PATH) == '1':
        off_icon = QIcon(resource_path(dmoff_icon))
        tray.setIcon(off_icon)
        tray.setToolTip("Darkmode")
    elif get_reg('SystemUsesLightTheme', REG_PATH) == '0':
        on_icon = QIcon(resource_path(dmon_icon))
        tray.setIcon(on_icon)
        tray.setToolTip("Darkmode")
    else:
        icon = QIcon(resource_path(dm_cfg))
        tray.setIcon(icon)
        tray.setToolTip("Darkmode - icon changes when you change mode!")
except WindowsError:
    pass
tray.setVisible(True)



#darkmode on
menu = QMenu()
dm_on = QAction(QIcon(dmon_icon),"Darkmode On")
menu.addAction(dm_on)
dm_on.triggered.connect(cmd_dmon)
#darkmode off

dm_off = QAction(QIcon(dmoff_icon),"Darkmode Off")
menu.addAction(dm_off)
dm_off.triggered.connect(cmd_dmoff)
# Settings

configw = QAction(QIcon(settings_icon),"Settings")
menu.addAction(configw)
configw.triggered.connect(cmd_config)

# Quit app
dmquit = QAction(QIcon(mn_exit),"Exit")
dmquit.triggered.connect(app.quit)
menu.addAction(dmquit)

# Add the menu to the tray
tray.setContextMenu(menu)


app.exec_()
