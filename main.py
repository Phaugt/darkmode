from PyQt5 import uic
from PyQt5.QtWidgets import (QAction, QApplication, QLineEdit, QMessageBox, QWidget, QLabel,
             qApp, QSystemTrayIcon, QMenu)
from PyQt5.QtCore import (QFile, QTime)
from PyQt5.QtGui import QIcon, QPixmap, QImage
from easysettings import EasySettings
import sys, os, winreg, greet, PyQt5, threading, time, schedule
from win10toast import ToastNotifier
from os.path import expanduser

#icon taskbar
try:
    from PyQt5.QtWinExtras import QtWin
    myappid = 'darkmode.python.schedule.program'
    QtWin.setCurrentProcessExplicitAppUserModelID(myappid)    
except ImportError:
    pass

#pyinstaller
def resource_path(relative_path):
    """is used for pyinstaller so it can read the relative path"""
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath('.'), relative_path)

#resources
dmon_icon = resource_path("./icons/dm_on.png") #darkode on
dmoff_icon = resource_path("./icons/dm_off.png") #darkmode off
dmon_ico = resource_path("./icons/dm_on.ico") #darkode on
dmoff_ico = resource_path("./icons/dm_off.ico") #darkmode off
settings_icon = resource_path("./icons/settings.png")
settings_ico = resource_path("./icons/settings.ico")
config_gui = resource_path("./gui/config.ui")
userfold = expanduser("~")
config = EasySettings(userfold+"./darkmode.conf")
dm_cfg = resource_path("./icons/dm_cfg.png") #no settings provided
dm_cfg_ico = resource_path("./icons/dm_cfg.ico") #no settings provided
mn_exit = resource_path("./icons/exit.png")
logo = resource_path("./icons/logo.png")
logo_ico = resource_path("./icons/logo.ico")
cfg_bg = resource_path("./gui/bg.png")
dm_enab = resource_path("./icons/dm_enab.png")
dm_vers = 'v.1.05 - 2021-03-31'
REG_PATH = r'SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Themes\\Personalize' #win theme
START_PATH = r'SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Run' #for autostart with windows


app = QApplication([])
app.setQuitOnLastWindowClosed(False)
toaster = ToastNotifier()


def notification(message, ico):
    """Windows10 notification"""
    toaster.show_toast("Darkmode",
                   message,
                   icon_path=ico,
                   duration=3,
                   threaded=True)


#failsafe first run
try:
    firstrn = config.get("first_run")
    if firstrn == "":
        config.set("first_run", "No")
        config.set("dark_start","00:00")
        config.set("dark_stop","00:00")
        config.save()
except Exception:
    notification("Error with Config file", dm_cfg_ico)

#config window
class Config(QWidget):
    """Config window - called from taskbar"""
    def __init__(self):
        super().__init__()
        UIFile = QFile(config_gui)
        UIFile.open(QFile.ReadOnly)
        uic.loadUi(UIFile, self)
        UIFile.close()

        #get settings
        try:
            if config.get("first_run") == "No":
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
                if config.get('Autostart') == 'Yes':
                    self.autoStart.setChecked(True)
                else:
                    self.autoStart.setChecked(False)
        except Exception:
            notification("Error with Config file", dm_cfg_ico)

        #buttons
        self.saveexit.clicked.connect(self.SaveConfigExit)
        self.saveexit.clicked.connect(lambda: w.stopSched())
        self.saveexit.clicked.connect(lambda: w.cmd_Schedule("Saved settings to file!"))
        self.saveconfig.clicked.connect(self.SaveConfig)
        self.saveconfig.clicked.connect(lambda: w.stopSched())
        self.saveconfig.clicked.connect(lambda: w.cmd_Schedule("Saved settings to file!"))
        self.clear.clicked.connect(self.cmd_clear)
        self.alt_username.setToolTip("Requires a restart of Darkmode when changed!")
        self.autoStart.stateChanged.connect(self.cmd_autoStart)

    def cmd_autoStart(self):
        name = 'Darkmode'
        cd = os.getcwd()
        cmd = (cd+"\\Darkmode.exe")
        if self.autoStart.isChecked():
            try:
                set_reg(name,cmd,START_PATH, winreg.REG_SZ)
                config.set("Autostart","Yes")
                config.save()
            except WindowsError:
                notification("Could not create registry key!",dm_cfg_ico)
        else:
            try:
                del_reg(name, START_PATH)
                config.set("Autostart","No")
                config.save()
            except WindowsError:
                notification("Could not delete registry key!",dm_cfg_ico)


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
            notification("Error with Config file", dm_cfg_ico)


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
            notification("Error with Config file", dm_cfg_ico)

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

def del_reg(name, path):
    """#delete winreg"""
    #thanks to tautulli code
    try:
        registry_key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, path, 0, winreg.KEY_ALL_ACCESS)
        winreg.QueryValueEx(registry_key, name)
        reg_value_exists = True
    except WindowsError:
        reg_value_exists = False

    if reg_value_exists:
        try:
            winreg.DeleteValue(registry_key, name)
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
    mode_icon = QIcon(set_icon)
    tray.setIcon(mode_icon)
    set_reg('AppsUseLightTheme', state, REG_PATH, winreg.REG_DWORD)
    set_reg('SystemUsesLightTheme', state, REG_PATH, winreg.REG_DWORD)
    if state == 0:
        notification(greet.greetdark, dmon_ico)
    else:
        notification(greet.greetlight, dmoff_ico)


def cmd_config():
    """#calls QWidget"""
    c.show()
    cf_bg = QPixmap(cfg_bg)
    c.bg.setPixmap(cf_bg)
    c.setWindowIcon(QIcon(logo_ico))
    c.dmVersion.setText(dm_vers)

# Create the tray
tray = QSystemTrayIcon()
try:
    icon = QIcon(logo)
    tray.setIcon(icon)
    tray.setToolTip("Darkmode")
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


class Worker():
    """worker class"""
    start_schedule = ContinuousScheduler()
    stop_schedule = ContinuousScheduler()
    stopDm1 = object
    stopDm2 = object


    def cmd_Schedule(self, message):
        """to enable schedule worker in separate threads in background"""
        enable = (config.get("dark_start"))
        disable = (config.get("dark_stop"))

        self.start_schedule.every().day.at(str(enable)).do(cmd_dmode, state=0,set_icon=dmon_ico)
        self.stopDm1 = self.start_schedule.run_continuously()
        

        self.stop_schedule.every().day.at(str(disable)).do(cmd_dmode, state=1,set_icon=dmoff_ico)
        self.stopDm2 = self.stop_schedule.run_continuously()

        notification(message,settings_ico)

    def stopSched(self):
        """to kill the runnings jobs and application"""
        self.stopDm1.set()
        self.stopDm1.clear()
        self.start_schedule.clear()
        self.stopDm2.set()
        self.stopDm2.clear()
        self.stop_schedule.clear()
    

#to enable the schedule when starting the application
w = Worker()
w.cmd_Schedule("Settings loaded from file!")

#menu
menu = QMenu()
#darkmode on
sched = QAction(QIcon(dm_enab),"Enable Schedule")
menu.addAction(sched)
sched.triggered.connect(lambda: w.stopSched())
sched.triggered.connect(lambda: w.cmd_Schedule("Schedule enabled, settings loaded!"))
#darkmode on
dm_on = QAction(QIcon(dmon_icon),"Darkmode On")
menu.addAction(dm_on)
dm_on.triggered.connect(lambda: cmd_dmode(0, dmon_icon))

#darkmode off
dm_off = QAction(QIcon(dmoff_icon),"Darkmode Off")
menu.addAction(dm_off)
dm_off.triggered.connect(lambda: cmd_dmode(1,dmoff_icon))
# Settings

configw = QAction(QIcon(settings_icon),"Settings")
menu.addAction(configw)
configw.triggered.connect(cmd_config)

# Quit app
dmquit = QAction(QIcon(mn_exit),"Exit")
dmquit.triggered.connect(lambda: w.stopSched())
dmquit.triggered.connect(app.quit)
menu.addAction(dmquit)

# Add the menu to the tray
tray.setContextMenu(menu)


app.exec_()
