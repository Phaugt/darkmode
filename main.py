from PyQt5 import uic
from PyQt5.QtWidgets import (QAction, QApplication, QLineEdit, QMessageBox, QWidget, QLabel,
             QToolButton, QErrorMessage, qApp, QToolBar,
            QStatusBar, QSystemTrayIcon, QMenu, QTimeEdit)
from PyQt5.QtCore import (QFile, QPoint, QRect, QSize, Qt, QTime,
            QProcess, QThread, pyqtSignal, pyqtSlot, Q_ARG , Qt, QMetaObject,
            QObject)
from PyQt5.QtGui import QIcon, QFont, QClipboard, QPixmap, QImage
from easysettings import EasySettings, esGetError, esError, esSaveError, esSetError
import sys, os, winreg, greet, PyQt5, threading, time, schedule
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
    """is used for pyinstaller so it can read the relative path"""
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
dm_cfg = resource_path("./icons/dm_cfg.png") #no settings provided
mn_exit = resource_path("./icons/exit.png")
REG_PATH = r'SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Themes\\Personalize' #reg path values changed for windows theme
#EDGE_PATH = r'SOFTWARE\\Classes\\Local Settings\\Software\\Microsoft\\Windows\\CurrentVersion\\AppContainer\\Storage\\microsoft.microsoftedge_8wekyb3d8bbwe\\MicrosoftEdge\\Main' #old edge not chromium based

#App
app = QApplication([])
app.setQuitOnLastWindowClosed(False)
toaster = ToastNotifier()


def notification(message, ico):
    """Windows10 notification"""
    toaster.show_toast("Darkmode",
                   message,
                   icon_path=ico,
                   duration=5,
                   threaded=True)


#config window
class Config(QWidget):
    """Config window - called from taskbar"""
    def __init__(self):
        super().__init__()
        UIFile = QFile(resource_path(config_gui))
        UIFile.open(QFile.ReadOnly)
        uic.loadUi(UIFile, self)
        UIFile.close()

    
        #default settings
        try:
            if config.get("first_run") == "Yes":
                on = self.time_dmon.time().toString("hh:mm")
                off = self.time_dmoff.time().toString("hh:mm")
                config.set("dark_start",str(on))
                config.set("dark_stop",str(off))
                config.set("first_run","No")
                config.save()
            else:
                on = config.get("dark_start")
                off = config.get("dark_stop")
                alt_user = config.get("username")
                if on == '00:00':
                    on = QTime(0,0)
                    self.time_dmon.setTime(on)
                elif on[-2:] == '00':
                    on = QTime(int(on[0:2]),0)
                    self.time_dmon.setTime(on)
                else:
                    on = QTime(int(on[0:2]),int(on[-2:]))
                    self.time_dmon.setTime(on)
                if off == '00:00':
                    off = QTime(0,0)
                    self.time_dmoff.setTime(off)
                elif off[-2:] == '00':
                    off = QTime(int(off[0:2]),0)
                    self.time_dmoff.setTime(off)
                else:
                    off = QTime(int(off[0:2]),int(off[-2:]))
                    self.time_dmoff.setTime(off)
                self.alt_username.setText(alt_user)
        except Exception:
            notification("Error with Config file", settings_ico)

        #buttons
        self.saveexit.clicked.connect(self.SaveConfigExit)
        self.saveexit.clicked.connect(lambda: worker.cmd_Schedule())
        self.saveconfig.clicked.connect(self.SaveConfig)
        self.saveconfig.clicked.connect(lambda: worker.cmd_Schedule())
        self.clear.clicked.connect(self.cmd_clear)
        self.alt_username.setToolTip("Requires a restart of Darkmode when changed!")

    def SaveConfigExit(self):
        """Save config to file and exit config window"""
        try:
            on = self.time_dmon.time().toString("hh:mm")
            off = self.time_dmoff.time().toString("hh:mm")
            user = self.alt_username.text()
            config.set("dark_start",str(on))
            config.set("dark_stop",str(off))
            config.set("username",str(user))
            config.set("saved_state","yes")
            config.save()
            c.close()
        except Exception:
            notification("Error with Config file", settings_ico)


    def SaveConfig(self):
        """Save config to file and keep window open"""
        try:
            on = self.time_dmon.time().toString("hh:mm")
            off = self.time_dmoff.time().toString("hh:mm")
            user = self.alt_username.text()
            config.set("dark_start",str(on))
            config.set("dark_stop",str(off))
            config.set("username",str(user))
            config.set("saved_state","yes")
            config.save()
        except Exception:
            notification("Error with Config file", settings_ico)

    def cmd_clear(self):
        """Clear config window content"""
        self.time_dmon.setTime(QTime(0,0))
        self.time_dmoff.setTime(QTime(0,0))
        self.alt_username.clear()
#to call config window
c = Config()

def set_reg(name, value, path, reg_type):
    """#change winreg"""
    try:
        winreg.CreateKey(winreg.HKEY_CURRENT_USER, path)
        registry_key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, path, 0, 
                                       winreg.KEY_WRITE)
        winreg.SetValueEx(registry_key, name, 0, reg_type, value)
        winreg.CloseKey(registry_key)
        return True
    except WindowsError:
        return False


def get_reg(name, path):
    """#check winreg"""
    state = 0
    try:
        registry_key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, path, 0,
                                       winreg.KEY_READ)
        state, regtype = winreg.QueryValueEx(registry_key, name)
        winreg.CloseKey(registry_key)
        return state
    except WindowsError:
        return None


def cmd_dmode(state, set_icon):
    """#sets darkmode on and changes icon"""
    mode_icon = QIcon(resource_path(set_icon))
    tray.setIcon(mode_icon)
    set_reg('AppsUseLightTheme', state, REG_PATH, winreg.REG_SZ)
    set_reg('SystemUsesLightTheme', state, REG_PATH, winreg.REG_SZ)
    if state == '0':
        notification(greet.greetdark, dmon_ico)
    else:
        notification(greet.greetlight, dmoff_ico)
    #set_reg('Theme', int(0), EDGE_PATH, winreg.REG_DWORD) #old edge not chromium based


def cmd_config():
    """#calls QWidget"""
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
        tray.setToolTip("Darkmode (icon will change when you change mode!)")
except WindowsError:
    pass
tray.setVisible(True)


class ContinuousScheduler(schedule.Scheduler):
    """this is a class which uses inheritance to act as a normal Scheduler,
        but also can run_continuously() in another thread"""
        #https://stackoverflow.com/questions/46453938/python-schedule-library-needs-to-get-busy-loop
    def run_continuously(self, interval=1):
            """Continuously run, while executing pending jobs at each elapsed
            time interval.
            @return cease_continuous_run: threading.Event which can be set to
            cease continuous run.
            Please note that it is *intended behavior that run_continuously()
            does not run missed jobs*. For example, if you've registered a job
            that should run every minute and you set a continuous run interval
            of one hour then your job won't be run 60 times at each interval but
            only once.
            """
            cease_continuous_run = threading.Event()

            class ScheduleThread(threading.Thread):
                """The job that should run continuous"""
                @classmethod
                def run(cls):
                    # I've extended this a bit by adding self.jobs is None
                    # now it will stop running if there are no jobs stored on this schedule
                    while not cease_continuous_run.is_set() and self.jobs:
                        # for debugging
                        # print("ccr_flag: {0}, no. of jobs: {1}".format(cease_continuous_run.is_set(), len(self.jobs)))
                        self.run_pending()
                        time.sleep(interval)

            continuous_thread = ScheduleThread()
            continuous_thread.start()
            return cease_continuous_run


class worker(QObject):
    """worker class"""
    def cmd_Schedule():
        """to enable schedule worker in separate threads in background"""
        enable = (config.get("dark_start"))
        disable = (config.get("dark_stop"))
        start_schedule = ContinuousScheduler()
        stop_schedule = ContinuousScheduler()
        start_schedule.every().day.at(str(enable)).do(cmd_dmode, state='0',icon=dmon_ico)
        start_schedule.run_continuously()
        stop_schedule.every().day.at(str(disable)).do(cmd_dmode, state='1',icon=dmoff_ico)
        stop_schedule.run_continuously()
        notification("Schedule enabled, will trigger Darkmode from settings",settings_ico)

    def killthread():
        """to kill the runnings jobs and application"""
        ContinuousScheduler.clear
        schedule.CancelJob()
        schedule.clear()
        worker.stop_schedule.set()
        worker.start_schedule.set()
        sys.exit()

#to enable the schedule when starting the application
worker.cmd_Schedule()

#menu
menu = QMenu()
#darkmode on
sched = QAction(QIcon(settings_icon),"Enable Schedule")
menu.addAction(sched)
sched.triggered.connect(lambda: worker.cmd_Schedule())
#darkmode on
dm_on = QAction(QIcon(dmon_icon),"Darkmode On")
menu.addAction(dm_on)
dm_on.triggered.connect(lambda: cmd_dmode('0', resource_path(dmon_icon)))

#darkmode off
dm_off = QAction(QIcon(dmoff_icon),"Darkmode Off")
menu.addAction(dm_off)
dm_off.triggered.connect(lambda: cmd_dmode('1',resource_path(dmoff_icon)))
# Settings

configw = QAction(QIcon(settings_icon),"Settings")
menu.addAction(configw)
configw.triggered.connect(cmd_config)

# Quit app
dmquit = QAction(QIcon(mn_exit),"Exit")
dmquit.triggered.connect(app.quit)
dmquit.triggered.connect(lambda: worker.killthread())
menu.addAction(dmquit)

# Add the menu to the tray
tray.setContextMenu(menu)


app.exec_()
