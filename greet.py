import getpass
import random
from easysettings import EasySettings
config = EasySettings("./config/config.conf")

if config.get("username") is "":
    username = getpass.getuser()
else:
    username = config.get("username")



Darkside = ["Welcome to the dark side "+username+"!",
            "Welcome to the dark side "+username+" we lied about the cookies!",
            "Welcome to the dark side "+username+" we have cookies!",
            "The darkside has cookies "+username+"!"]

Lightside =["Welcome to the light "+username+"!",
            username+" the light side has cookies too!",
            "We do not lie about the cookies "+username+"!",
            "Welcome to the light side of the moon "+username+"!"]

greetlight = random.choice(Lightside)
greetdark = random.choice(Darkside)
