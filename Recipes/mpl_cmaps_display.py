# -*- coding: utf-8 -*-

# Module: mpl_cmaps_display

import numpy as np
from matplotlib import pyplot as plt
import matplotlib.gridspec as gridspec
from collections import OrderedDict
from enum import Enum, unique
            
CMAPS_DICT = OrderedDict()
#
# Note: Function plot_cmaps_grids depends on this order:
#
CMAPS_DICT['Sequential 1'] = [
            'Greys', 'Purples', 'Blues', 'Greens', 'Oranges', 'Reds',
            'YlOrBr', 'YlOrRd', 'OrRd', 'PuRd', 'RdPu', 'BuPu',
            'GnBu', 'PuBu', 'YlGnBu', 'PuBuGn', 'BuGn', 'YlGn']

CMAPS_DICT['Sequential 2'] = [
            'binary', 'gist_yarg', 'gist_gray', 'gray', 'bone', 'pink',
            'spring', 'summer', 'autumn', 'winter', 'cool', 'Wistia',
            'hot', 'afmhot', 'gist_heat', 'copper']

CMAPS_DICT['Perceptually Uniform Sequential'] = [
            'viridis', 'plasma', 'inferno', 'magma', 'cividis']

CMAPS_DICT['Diverging'] = [
            'PiYG', 'PRGn', 'BrBG', 'PuOr', 'RdGy', 'RdBu',
            'RdYlBu', 'RdYlGn', 'Spectral', 'coolwarm', 'bwr', 'seismic']

CMAPS_DICT['Qualitative'] = ['Pastel1', 'Pastel2', 'Paired', 'Accent',
                        'Dark2', 'Set1', 'Set2', 'Set3',
                        'tab10', 'tab20', 'tab20b', 'tab20c']

CMAPS_DICT['Cyclic'] = ['flag', 'prism', 'twilight', 'twilight_shifted', 'hsv']

CMAPS_DICT['Miscellaneous'] = [
             'ocean', 'gist_earth', 'terrain', 'gist_stern',
            'gnuplot', 'gnuplot2', 'CMRmap', 'cubehelix', 'brg',
            'gist_rainbow', 'rainbow', 'jet', 'nipy_spectral', 'gist_ncar']


@unique
class CMAP_CAT(Enum):
    """
    Data entry helper for accessing CMAPS_DICT keys.
    """
    SEQ1 = 'Sequential 1'
    SEQ2 = 'Sequential 2'
    SEQ3 = 'Perceptually Uniform Sequential'
    DIVERG = 'Diverging'
    QUALIT = 'Qualitative'
    CYCLIC = 'Cyclic'
    MISC = 'Miscellaneous'


def show_cmap_cat_shortnames():
    txt = 'CMAP_CAT.shortname: key'
    for name, membr in CMAP_CAT.__members__.items():
        txt += '\n{:>18}: {}'.format(name, membr.value)
    print(txt)


def _plot_colormap(ax, img_vect, cm_name, color_map):
    """
    Using the given axis and color vector, plot the colors in the 
    color map object `color_map` named `cm_name`, and display the name
    and map size to the left.
    """
    ax.imshow(img_vect, aspect='auto', cmap=color_map)
    pos = list(ax.get_position().bounds)
    x_text = pos[0] - 0.01
    y_text = pos[1] + pos[3]/2.
    txt = f'{cm_name} {color_map.N} '
    ax.text(x_text, y_text, txt, va='center', ha='right', fontsize=10)
    ax.set_axis_off()
    

def plot_cmap_cat(cm_category:CMAP_CAT, fig_size=(8,4), save_file=None):
    """
    Plot a single Matplotlib (3.1.1) color map category using its 
    short name defined in Enum class CMAP_CAT.
    Input:
        cmap_category: color map category.
        fid_size: (w, h) tuple.
        save_file: picture filename if not None.
    Output:
        A plot displaying the color maps in given camp_category.
    """
    if isinstance(cm_category, str):
        print("`cm_category` must refer to the CMAP_CAT shortname:")
        show_cmap_cat_shortnames()
        return
        
    cm_cat = cm_category.value
    cmap_list = CMAPS_DICT[cm_cat]
    nro = len(cmap_list)

    gradient = np.linspace(0, 1, 256)
    gradient = np.vstack((gradient, gradient))
    
    fig, axes = plt.subplots(nrows=nro, figsize=fig_size)
    axes[0].set_title(cm_cat + ' colormaps', fontsize=12)
    
    for axi, cm_name in zip(axes, cmap_list):
        cm = plt.get_cmap(cm_name)
        _plot_colormap(axi, gradient, cm_name, cm)
        
    if save_file is not None:
        # no other check on filename!
        plt.savefig(save_file,
                    transparent=True,
                    bbox_inches='tight',
                    pad_inches=0.0)
    plt.show();
    
    
def _plot_cmaps_gradients(fig, gsi, gradient, cm_category):
    """
    Accessory function for `plot_cmaps_grids`
    """
    
    cmap_list = CMAPS_DICT[cm_category]
    nro = len(cmap_list)
    gs = gsi.subgridspec(nro, 1)

    for i, cm_name in enumerate(cmap_list):
        axi = fig.add_subplot(gs[i, 0])
        if i == 0:
            axi.set_title(cm_category + ' colormaps', fontsize=12)

        cm = plt.get_cmap(cm_name)
        _plot_colormap(axi, gradient, cm_name, cm)


def plot_cmaps_grids(fig_size=(17,7), save_file=None):
    """
    Plot Matplotlib (3.1.1) color maps in a grid plot.
    Code refactored from User Guide: 
         https://matplotlib.org/tutorials/colors/colormaps.html
    
    Input:
        fid_size: (w, h) tuple.
        save_file: picture filename is not None.
        (Uses module CMAPS_DICT.)
    Output:
        A compact grid plot displaying 7 categories of color maps.
    """
    f = plt.figure(figsize=fig_size)

    gradient = np.linspace(0, 1, 256)
    # Need 2D for ax.imshow:
    gradient = np.vstack((gradient, gradient))

    gs = gridspec.GridSpec(4, 3, figure=f, wspace=0.42)

    # Note: if the order in cmaps dict changes, then this
    #       assignment may need to change as well:
    for key, gsi in zip(CMAPS_DICT.keys(),
                        [gs[:2,0], gs[:2,1], gs[0,-1],
                         gs[2:,0], gs[2:,1], gs[1,-1], gs[2:,-1]]
                       ):
        _plot_cmaps_gradients(f, gsi, gradient, key)
        
    if save_file is not None:
        # no other check on filename!
        plt.savefig(save_file,
                    transparent=True,
                    pad_inches=0.0)
    plt.show();

    
__all__ = ['CMAPS_DICT', 'CMAP_CAT', 
           'show_cmap_cat_shortnames',
           'plot_cmap_cat',
           'plot_cmaps_grids']


if __name__ == '__main__':
    plot_cmaps_grids()
    