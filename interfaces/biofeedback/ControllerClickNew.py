from Tkinter import *
import time

class ControllerClick(Tk):
    def __init__(self,  window_size=(490, 490), number = 3, pause = 2, time_exp=4):
        Tk.__init__(self)
        fr = Frame(self)
        fr.pack()
        self.window_x, self.window_y = window_size
        self.config = {}
        self.number = number
        self.time_exp = time_exp
        self.counter = 0
        self.pause_time = pause        
        self.canvas  = Canvas(fr, height=self.window_x, width=self.window_y, bg="white")
        self.canvas.bind("<Motion>", self.motion)
        self.canvas.bind("<ButtonPress-1>", self.button_press)
        self.canvas.pack()
        self.do_exp = False
        start_button = Button(self, text="start exp", 
                              command=self.start_exp)
        start_button.pack()

        self.pouse = False

    def button_press(self, event):
        if self.button_press == 'up':
            self.button_press = "down"
            self.after(self.time_exp*1000, self.exp_pouse)
            self.task_timestamps.append(time.time())  

    def motion(self, event):
        if self.button_press == "down":
            if self.x_position is not None and self.y_position is not None:
                event.widget.create_line(self.x_position, self.y_position, event.x, event.y, smooth=True)
            self.x_position = event.x
            self.y_position = event.y
            self.mouse_positions.append((self.x_position, self.y_position)) 

    def exp_pouse(self):
        self.button_press = "up"
        self.x_position = None
        self.y_position = None
        self.task_timestamps.append(time.time())
        self.update_config()
        if self.counter == self.number:
            self.quit()
        self.canvas.delete(ALL) 
        self.after(self.pause_time*1000, self.exp)

    def start_exp(self):
        self.exp()

    def _setup_oval_params(self):
        self.button_press = "up"
        self.x_position = None
        self.y_position = None
        self.task_timestamps = []
        self.mouse_positions = []
        self.counter +=1

    def exp(self):
        self.oval = self.canvas.create_oval(20, 20, self.window_x-30, self.window_y-30, outline="red", fill="white", width=2)
        self.oval2 = self.canvas.create_oval(self.window_x/2-4, 20-4,self.window_x/2+4, 20+4, outline="blue", fill="blue", width=2)
        self._setup_oval_params()

    def update_config(self):
        self.config["{}".format(self.counter)] = (self.task_timestamps, self.mouse_positions)
    

    def get_config(self):
        return self.config


if __name__ == "__main__":
    root = ControllerClick()
    root.mainloop()
    print root.get_config()