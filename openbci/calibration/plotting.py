import matplotlib.pyplot as plt
import numpy as np
from matplotlib import collections, axes, transforms, text, patches
import experiment_builder.experiment_tag_utils as exp_utils
from mpl_toolkits.axes_grid import AxesGrid

diag_colors = ['#FF0000','#FFFF00','#00FF00','#00FFFF',
               '#0000FF','#FAAC58','#000000','#A4A4A4','#FA58F4']

def draw_basic_bars_spectrum(ax, freqs, amplitudes, width, tags=None, props=None):
    """
    Draw bars diagram for frequencies and their amplitudes.
    """
    size = None
    if props:
        if props.has_key('fig_title'):
            ax.figure.suptitle(props['fig_title'], color='r')
        if props.has_key('ax_title'):
            if props.has_key('ax_title_size'):
                ax.set_title(props['ax_title'], size=props['ax_title_size'])
            else:
                ax.set_title(props['ax_title'])
        else:
            ax.set_title('Spectrum')
        if props.has_key('axes_titles'):
            if props['axes_titles']:
                ax.set_ylabel('Amplitudes')
                ax.set_xlabel('Selected frequencies')
        if props.has_key('font_size'):
            size = props['font_size']
                
    xs = np.arange(len(freqs))
    ax.set_xticks(xs)
    ax.set_xticklabels([('%g'%fr) for fr in freqs], rotation=45, size=size)
    
    rects = ax.bar(xs+0.6*width, amplitudes, width, color='#A4A4A4')
    
    max_amp = max(amplitudes)
    min_amp = min(amplitudes)
    y_offset = 0.01*(max_amp-min_amp)
    for r in rects:
        y = r.get_height()
        ax.text(r.get_x()+float(width)/2, y, '%f'%y, 
                ha='center', va='bottom', rotation=45, color='b', size=size)

    return ax


def draw_bars_single_freq(ax, freqs, amplitudes, width, tags, squares=False, props=None):
    """
    Draw bars diagram for single freqs round of calibration.
    Amplitudes for freqs are drawn in chronological order,
    displayed info on freq disp.time, break time and field number.
    """

    ax = draw_basic_bars_spectrum(ax, freqs, amplitudes, width, props=props)
    
    # Draw information of screen squares 
    if squares:
        w = ax.get_xlim()[1]
        h= ax.get_ylim()[1]
        
        ax.set_xlim([0, w + 0.7])
        ax.set_ylim([0, h + 1.7*(h/10)])  
        w = ax.get_xlim()[1]
        h = ax.get_ylim()[1]
        l = len(tags)
        bboxes = []
        for i in range(l):
            bboxes.append(transforms.Bbox(np.array([[i+0.1, h-(1.3*h/10)], [(i+1)-0.1, h-(0.3*h/10)]])))
        
            rects, texts = square_info( tags[i], bboxes[i], ax)
    

def draw_bars_multi_freq_sequence(chunks, tags, width, squares=False, props=None): 
    """
    Draw diagram of differences (from stat_analyse) for every frequency tested 
    (in order of fields of concentration).
    """
    num_axes = len(chunks) # assuming 8 :-)
    fig = plt.figure()
    axes = []
    
    max_val = 0
    max_val_ind = 0
    for i in range(len(chunks)):
        ch = chunks[i]
        m = max(ch[0])
        if m > max_val:
            max_val = m 
            max_val_ind = i
    md = np.ceil(max_val)  
    
    ma = fig.add_subplot(2, np.ceil(num_axes/2), max_val_ind+1)
    last = ma
    for i in range(num_axes):
        if i == max_val_ind:
            axes.append(ma)
            last = ma
        else:
            a = fig.add_subplot(2, np.ceil(float(num_axes)/2), i+1, sharey=last)
            axes.append(a)
            last = a
            
    fig.subplots_adjust(bottom=0.07, left=0.05, right=0.95)

    if props:
        fig.suptitle(props['fig_title'], color='r')

    
    for ax, chunk, tag in zip(axes, chunks, tags):
        
        freqs, square_no, delay = exp_utils.basic_params(tag)
        
        prp = {}
        prp['ax_title'] = '%f' % tag['start_timestamp'] + ' - ' + '%f' % (tag['start_timestamp'] + delay)
        prp['ax_title_size'] = 'x-small'
        prp['axes_titles'] = False
        prp['font_size'] = 'x-small'
        ax = draw_basic_bars_spectrum(ax, chunk[1], chunk[0], width, tags=None, props=prp)
        
        [hmin, hmax] = ax.get_ybound()
        ax.set_ybound([hmin, 1.2*hmax])
        [nmin, nmax] = ax.get_ybound()
        w = ax.get_xbound()[1]
        
        xax = ax.get_xaxis()
        w = max(xax.get_majorticklocs())+1
        yax = ax.get_yaxis()
        h = 1.1*md#max(yax.get_majorticklocs())+1
        bbox = transforms.Bbox(np.array([[w/2-0.15*w, 0.81*h], [w/2+0.15*w, 0.95*h]]))
        rects, texts = square_info(tag, bbox, ax)

    
def draw_multi_freq(chunks, tags, squares=False, props=None):
    """
    Draw point diagram of differences (from stat_analyse) for every frequency tested 
    all lines on one drawing.
    """
    fig = plt.figure()
    if props:
       if props.has_key('fig_title'):
           fig.suptitle(props['fig_title'], color='r')
    lines = []
    
    ax = fig.add_subplot(111)
    ax.grid(color='#aaaaaa', linestyle=':')
    colors = diag_colors[:len(chunks[0][1])]

    for chunk, col, tag in zip(chunks, colors, tags):
        lines.append(plt.plot(chunk[1], chunk[0], 'o-', color=col))
    legends = []
    for tag in tags:
        freqs, n, delay = exp_utils.basic_params(tag)
        legends.append(str(freqs)+" Sq.no: " + str(n+1) + '/ Fr: ' + '%g'%freqs[n])
    ax.legend(lines, legends, loc=0, prop={'size' : 'x-small'})
    
            
    
def square_info(p_exp_tag, bbox, axes):
    """
    Draw scheme of the blinking screen, with freqs info and current square.
    """
    t_freqs, square_no, delay = exp_utils.basic_params(p_exp_tag)
    bounds = bbox.get_points()
    rects = []
    texts = []
    x_size = (bounds[1][0] - bounds[0][0])/4
    y_size = (bounds[1][1] - bounds[0][1])/2
    start = bounds[0]
    for y in range(2):
        for x in range(len(t_freqs)/2):
            num = x + y*len(t_freqs)/2
            if (num == square_no):
                col = 'r'
            else:
                col = '#E2E2E2' 
            a = start[0]+x*x_size
            b = start[1]+(1-y)*y_size
            rects.append(patches.Rectangle((a, b), x_size, y_size, 
                                           facecolor=col, linestyle='solid', edgecolor='#333333',
                                           linewidth=1.))
            texts.append(text.Text(a + x_size/8, b+y_size/8, '%g'%t_freqs[num], color='k',
                                   size='small'))
    for r, t in zip(rects, texts):
        axes.add_patch(r)
        t.set_zorder(100)
        axes.add_artist(t)

    return rects, texts
                         
    
    
