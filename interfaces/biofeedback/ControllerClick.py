from Tkinter import *
import time

class ControllerClick:
    def __init__(self, master, window_size=(490, 490), number = 3, pause = 2):
        self.master = master
        self.window_x, self.window_y = window_size
        self.config = {}
        self.number = number
        self.counter = 0
        self.pause_time = pause
        self.C = Canvas(self.master, bg="white", height=self.window_x, width=self.window_y)
        self.C.bind("<Motion>", self.motion)
        self.C.bind("<ButtonPress-1>", self.button_press)

    def create_oval(self):
        self.oval = self.C.create_oval(20, 20, self.window_x-30, self.window_y-30, outline="red", fill="white", width=2)
        print self.oval
        self.C.pack()
        self._setup_oval_params()

    def _setup_oval_params(self):
        self.button_press = "up"
        self.x_position = None
        self.y_position = None
        self.task_timestamps = []
        self.mouse_positions = []
        self.counter +=1

    def update_config(self):
        self.config["{}".format(self.counter)] = (self.task_timestamps, self.mouse_positions)
    
    def pause(self):
        self.C.delete(ALL)
        self.C.pack()
        time.sleep(self.pause_time)

    def quit(self):
        self.master.destroy()

    def get_config(self):
        return self.config

    def button_press(self, event):
        if self.button_press == 'up':
            self.button_press = "down"
            self.task_timestamps.append(time.time())
        else:
            self.button_press = "up"
            self.x_position = None
            self.y_position = None
            self.task_timestamps.append(time.time())

            self.update_config()
            if self.counter == self.number:
                self.quit()
            else:
                self.pause()
                self.create_oval()     

    def motion(self, event):
        if self.button_press == "down":
            if self.x_position is not None and self.y_position is not None:
                event.widget.create_line(self.x_position, self.y_position, event.x, event.y, smooth=True)
            self.x_position = event.x
            self.y_position = event.y
            self.mouse_positions.append((self.x_position, self.y_position)) 


if __name__ == '__main__':
    number = 3
    pause = 2 
    root = Tk()
    my_gui = ControllerClick(root, number = number, pause = pause)
    my_gui.create_oval()
    root.mainloop()
    print my_gui.get_config()