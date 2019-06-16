#!/usr/bin/env python3

from evdev import InputDevice, categorize, ecodes
from time import sleep
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import urllib.request
import os
import threading

class Mainframe(tk.Tk):
    def __init__(self):
        tk.Tk.__init__(self)
        
        self.bind("<Right>", self.focusNextWidget)
        self.bind("<Left>", self.focusPreviousWidget)
        
        self.frame = GroboyGUI(self)
        self.frame.grid()

    def change(self, frame):
        self.frame = frame(self)
        self.frame.grid()

    def focusNextWidget(self, event):
        event.widget.tk_focusNext().focus_set()
        return("break")
        
    def focusPreviousWidget(self, event):
        event.widget.tk_focusPrev().focus_set()
        return("break")

class GroboyGUI(tk.Frame):
    def __init__(self, parent):
        tk.Frame.__init__(self, parent)
        self.parent = parent
        w = 320
        h = 240
        sw = self.parent.winfo_screenwidth()
        sh = self.parent.winfo_screenheight()
        x = (sw - w)/2
        y = (sh - h)/2
        self.parent.geometry('%dx%d+%d+%d' % (w, h, x, y))

        self.mainFrame = tk.Frame(self.parent)
        self.mainFrame.grid(row=0, column=0)
        self.mainFrame.bind_class("Button", "<x>", lambda event: event.widget.invoke())


        ###### Retroarch Icon ######
        retroarch = Image.open("images/retroarch.png")
        retroarch_icon = retroarch.resize((80, 80), Image.ANTIALIAS)
        retroarch_icon = ImageTk.PhotoImage(retroarch_icon)

        retroarch_button = tk.Button(self.mainFrame, image=retroarch_icon, highlightcolor="green", highlightthickness=5, command=self.startRetroarch)
        retroarch_button.image=retroarch_icon
        retroarch_button.grid(row=0, column=0, padx=(8,0), pady=(22,0), sticky=tk.N+tk.S+tk.E+tk.W)

        ###### Robot control ######
        robo_control = Image.open("images/cyberman.png")
        robo_control_icon = robo_control.resize((80, 80), Image.ANTIALIAS)
        robo_control_icon = ImageTk.PhotoImage(robo_control_icon)

        robo_control_button = tk.Button(self.mainFrame, image=robo_control_icon, highlightcolor="green", highlightthickness=5, command=self.grobotControl)
        robo_control_button.image=robo_control_icon
        robo_control_button.grid(row=0, column=1, padx=(8,0), pady=(22,0), sticky=tk.N+tk.S+tk.E+tk.W)
        
        ###### Shutdown ######
        shutdown_button = tk.Button(self.mainFrame, text="Shutdown", highlightcolor="green", highlightthickness=5, command=self.shutdown)
        shutdown_button.image=robo_control_icon
        shutdown_button.grid(row=0, column=2, padx=(8,0), pady=(22,0), sticky=tk.N+tk.S+tk.E+tk.W)

    def startRetroarch(self):
        os.system("SDL_NOMOUSE=1 retroarch -f")
        return("break")
        
    def grobotControl(self):
        for widget in self.parent.winfo_children():
            widget.grid_remove()
        self.parent.change(GrobotControl)
        
    def shutdown(self):
        os.system("sudo poweroff")
        return("break")
        
class GrobotControl(tk.Frame):
    def __init__(self, parent):
        tk.Frame.__init__(self, parent)
        self.parent = parent
        w = 320
        h = 240
        sw = self.parent.winfo_screenwidth()
        sh = self.parent.winfo_screenheight()
        x = (sw - w)/2
        y = (sh - h)/2
        self.parent.geometry('%dx%d+%d+%d' % (w, h, x, y))
        
        self.server_ip = "192.168.0.1"
        
        self.mainFrame = tk.Frame(self.parent)
        self.mainFrame.grid(row=0, column=0)
        
        self.bottomFrame = tk.Frame(self.parent)
        self.bottomFrame.grid(row=1, column=0)
        
        self.mainFrame.bind_class("Button", "<x>", lambda event: event.widget.invoke())
        self.bottomFrame.bind_class("Button", "<x>", lambda event: event.widget.invoke())
        
        joystick_thread = threading.Thread(target=self.readJoystick)
        joystick_thread.start()
        
        # Left Side
        
        forward_button = tk.Button(self.mainFrame, text="▲", font=('Helvetica', '14'),
            highlightcolor="green", highlightthickness=5, command=lambda: self.botCommand('forward'))
        forward_button.grid(row=0, column=1, padx=1, pady=(5,0), sticky=tk.N+tk.S+tk.E+tk.W)
        
        left_button = tk.Button(self.mainFrame, text="◀", font=('Helvetica', '14'),
            highlightcolor="green", highlightthickness=5)
        left_button.grid(row=1, column=0, padx=(1,0), pady=(1,0), sticky=tk.N+tk.S+tk.E+tk.W)
        
        right_button = tk.Button(self.mainFrame, text="▶", font=('Helvetica', '14'),
            highlightcolor="green", highlightthickness=5)
        right_button.grid(row=1, column=2, padx=(0,0), pady=(1,0), sticky=tk.N+tk.S+tk.E+tk.W)
        
        reverse_button = tk.Button(self.mainFrame, text="▼", font=('Helvetica', '14'),
            highlightcolor="green", highlightthickness=5, command=lambda: self.botCommand('reverse'))
        reverse_button.grid(row=2, column=1, padx=1, pady=(1,0), sticky=tk.N+tk.S+tk.E+tk.W)
        
        # Right Side
        
        raise_button = tk.Button(self.mainFrame, text="↥", font=('Helvetica', '14'), 
            highlightcolor="green", highlightthickness=5, command=lambda: self.botCommand('stand_up'))
        raise_button.grid(row=0, column=4, padx=1, pady=(5,0), sticky=tk.N+tk.S+tk.E+tk.W)
        
        rotate_left_button = tk.Button(self.mainFrame, text="↶", font=('Helvetica', '14'),
            highlightcolor="green", highlightthickness=5, command=lambda: self.botCommand('rotate_left'))
        rotate_left_button.grid(row=1, column=3, padx=(1,0), pady=(1,0), sticky=tk.N+tk.S+tk.E+tk.W)
        
        rotate_right_button = tk.Button(self.mainFrame, text="↷", font=('Helvetica', '14'),
            highlightcolor="green", highlightthickness=5, command=lambda: self.botCommand('rotate_right'))
        rotate_right_button.grid(row=1, column=5, padx=(0,0), pady=(1,0), sticky=tk.N+tk.S+tk.E+tk.W)
        
        lower_button = tk.Button(self.mainFrame, text="↧", font=('Helvetica', '14'),
            highlightcolor="green", highlightthickness=5, command=lambda: self.botCommand('sit'))
        lower_button.grid(row=2, column=4, padx=1, pady=(1,0), sticky=tk.N+tk.S+tk.E+tk.W)
        
        # Bottom Frame
        
        shutdown_bot_button = tk.Button(self.bottomFrame, text="Shutdown Bot", highlightcolor="green", highlightthickness=5, command=lambda: self.botCommand('poweroff'))
        shutdown_bot_button.grid(row=0, column=0, pady=(15,0))
        
        back_button = tk.Button(self.bottomFrame, text="Main Menu", highlightcolor="green", highlightthickness=5, command=self.mainMenu)
        back_button.grid(row=0, column=1, pady=(15,0))
        
    def readJoystick(self):
        device = InputDevice('/dev/input/event1')
        while True:
            for event in device.read_loop():
                if event.code == 1 and event.value <= 1500:
                    self.botCommand("forward")
                elif event.code == 1 and event.value >= 1800:
                    self.botCommand("reverse")
                elif event.code == 4 and event.value >= 1800:
                    self.botCommand("rotate_left")
                elif event.code == 4 and event.value <= 1500:
                    self.botCommand("rotate_right")
            time.sleep(0.05)
        
    def mainMenu(self):
        for widget in self.parent.winfo_children():
            widget.grid_remove()
        self.parent.change(GroboyGUI)
        
    def botCommand(self, action):
        try:
            urllib.request.urlopen("http://" + self.server_ip + ":5000/actions?action=" + action)
        except:
            pass

if __name__ == "__main__":
	app = Mainframe()
	app.wm_attributes('-fullscreen','true')
	app.mainloop()
