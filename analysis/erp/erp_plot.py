import pylab
import math
class Plotter(object):
    def __init__(self, x, y, fig_id=0):
        pylab.figure(fig_id)
        self.num_of_x = x
        self.num_of_y = y
        self.labels = {}
        self.plot_params = {}
    def add_plot(self, data, label, x, plot_id, title='', args={}):
        print("len(x): "+str(len(x))+", len(data):"+str(len(data)))
        assert(len(x) == len(data))
        pylab.subplot(self.num_of_x, self.num_of_y, plot_id)
        pylab.plot(x, data, **args)

        self.labels[plot_id] = self.labels.get(plot_id,[])
        self.labels[plot_id].append(label)

    def add_plot_param(self, plot_id, k, v):
        self.plot_params[plot_id] = self.plot_params.get(plot_id, {})
        self.plot_params[plot_id][k] = v

    def prepare_to_show(self, xlabel='time (ms)', ylabel='EEG (uV)', loc=4):
        for k, v in self.labels.iteritems():
            pylab.subplot(self.num_of_x, self.num_of_y, k)
            pylab.legend(v, loc=loc)
            title = self.plot_params.get(k, {}).get('title', '')
            pylab.title(title)
            pylab.xlabel(xlabel)
            pylab.ylabel(ylabel)


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
