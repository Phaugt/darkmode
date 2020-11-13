import getpass
import random
import main

if main.config.get('username') =="":
    loggedin = getpass.getuser()
else:
    loggedin = main.config.get('username')



Darkside = ["Welcome to the dark side "+loggedin+"!",
            "Welcome to the dark side "+loggedin+" we lied about the cookies!",
            "Welcome to the dark side "+loggedin+" we have cookies!",
            "The darkside has cookies "+loggedin+"!"]

Lightside =["Welcome to the light "+loggedin+"!",
            loggedin+" the light side has cookies too!",
            "We do not lie about the cookies "+loggedin+"!",
            "Welcome to the light side of the moon "+loggedin+"!"]

greetlight = random.choice(Lightside)
greetdark = random.choice(Darkside)
