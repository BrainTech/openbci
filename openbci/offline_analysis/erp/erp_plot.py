import pylab
import math
class Plotter(object):
    def __init__(self, x, y, fig_id=0):
        pylab.figure(fig_id)
        self.num_of_x = x
        self.num_of_y = y
        self.labels = {}
    def add_plot(self, data, label, x, plot_id):
        print("len(x): "+str(len(x))+", len(data):"+str(len(data)))
        assert(len(x) == len(data))
        pylab.subplot(self.num_of_x, self.num_of_y, plot_id)
        pylab.plot(x, data)


        self.labels[plot_id] = self.labels.get(plot_id,[])
        self.labels[plot_id].append(label)
        


    def prepare_to_show(self):
        for k, v in self.labels.iteritems():
            pylab.subplot(self.num_of_x, self.num_of_y, k)
            l = pylab.legend(v, loc=4)
            l.fontsize = 3

def show():
    pylab.show()


def test():
    x = 1
    y = 1
    i = 1
    plotter = Plotter(x, y, i)
    plotter.add_plot(range(10), 'nic', range(10),  i)
    plotter.add_plot(range(10,0,-1), 'cos',range(10), i)
    plotter.prepare_to_show()


    show()
    

if __name__ == "__main__":
    test()
