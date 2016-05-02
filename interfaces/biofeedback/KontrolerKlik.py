from Tkinter import *
import time

b1 = "up"
xold, yold = None, None
class KontrolerKlik(object):
    czasy = []
    wspolrzedne = []
    @staticmethod
    def on_button_press(event):
    	global b1
    	b1 = "down"
    	t0 = time.time()
    	KontrolerKlik.czasy.append(t0)
        print KontrolerKlik.czasy

    @staticmethod
    def on_doublebutton_press(event):
    	global b1, xold, yold
    	b1 = "up"
    	t1 = time.time()
    	xold = None          
    	yold = None
    	KontrolerKlik.czasy.append(t1)
        print KontrolerKlik.czasy
        print KontrolerKlik.wspolrzedne
	#KontrolerKlik.clear()

    #def clear(self):
	#self.C.delete(xold, yold)

    @staticmethod
    def motion(event):
        if b1 == "down":
            global xold, yold
            if xold is not None and yold is not None:
                event.widget.create_line(xold,yold,event.x,event.y,smooth=TRUE)
            xold = event.x
	    yold = event.y
	    KontrolerKlik.wspolrzedne.append((xold, yold))

    	   
    def __init__(self, rozmiar_okna = (490,490)):
        self.x, self.y = rozmiar_okna
	self.root = Tk()
	self.C = Canvas(self.root, bg="white", height=500, width=500)
    	oval = self.C.create_oval(10, 10, self.x, self.y, outline="red", fill="white", width=2)
    	self.C.pack()
    	self.C.bind("<Motion>", self.motion)
   	self.C.bind("<ButtonPress-1>", self.on_button_press)
    	self.C.bind("<Double-ButtonPress-1>", self.on_doublebutton_press)

	#d = C(self.root, text="Delete me", command=lambda: d.grid_remove())


    def run(self):
	self.root.mainloop() 
       
    	

if __name__ == "__main__":
    k = KontrolerKlik()
    k.run()

