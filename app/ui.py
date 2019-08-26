import pystray
import configparser
from PIL import Image, ImageDraw

def 

def quit_application(icon):
    icon.stop()

image = Image.open('static/logo.png')
menu = (pystray.MenuItem('Quit', quit_application), pystray.MenuItem('Help', quit_application))
icon = pystray.Icon('steamding', image, 'steamding', menu)

icon.run()