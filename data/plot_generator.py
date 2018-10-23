import matplotlib.pylab as plt
from matplotlib.colors import LogNorm
import matplotlib.patches as mpatches
from mpl_toolkits.axes_grid1.anchored_artists import AnchoredSizeBar
import matplotlib.font_manager as fm
from mpl_toolkits.axes_grid.inset_locator import inset_axes

import numpy as np
from numpy import in1d

from string import ascii_lowercase
import copy

from collections import namedtuple
import dill as pickle

import sys
sys.path.append('../')

from fdfdpy import Simulation
from structures import two_port, three_port, ortho_port
from device_saver import Device

scale_bar_pad = 0.75
scale_bar_font_size = 10
fontprops = fm.FontProperties(size=scale_bar_font_size)

def set_axis_font(ax, font_size):
    for item in ([ax.title, ax.xaxis.label, ax.yaxis.label] +
             ax.get_xticklabels() + ax.get_yticklabels()):
        item.set_fontsize(font_size)

def plot_Device(D):

    structure_type = D.structure_type
    if structure_type == 'two_port':
        f = plot_two_port(D)
    elif structure_type == 'three_port':
        f = plot_three_port(D)
    elif structure_type == 'ortho_port':
        f = plot_ortho_port(D)
    else:
        raise ValueError("Incorrect structure_type: {}".format(structure_type))
    return f


############################################################################################################################################
############################################################################################################################################
############################################################################################################################################
############################################################################################################################################

def plot_two_port(D):

    eps_disp, design_region = two_port(D.L, D.H, D.w, D.l, D.spc, D.dl, D.NPML, D.eps_m)
    f, (ax_top, ax_mid, ax_bot) = plt.subplots(3, 2, figsize=(7, 5), constrained_layout=True)

    # draw structure
    ax_drawing = ax_top[0]
    im = ax_drawing.pcolormesh(D.x_range, D.y_range, eps_disp.T, cmap='Greys')
    ax_drawing.set_xlabel('x position ($\mu$m)')
    ax_drawing.set_ylabel('y position ($\mu$m)')
    base_in = 9.5
    tip_in = 5.5
    y_shift = 0.05
    y_dist = 1.5    
    arrow_in = mpatches.FancyArrowPatch((-base_in, y_shift), (-tip_in, y_shift),
                                        mutation_scale=20, facecolor='#cc99ff')
    ax_drawing.add_patch(arrow_in)
    arrow_top = mpatches.FancyArrowPatch((tip_in, y_shift), (base_in, y_shift),
                                         mutation_scale=20, facecolor='#3366ff')
    ax_drawing.add_patch(arrow_top)
    arrow_bot = mpatches.FancyArrowPatch((tip_in, -y_dist), (base_in, -y_dist),
                                         mutation_scale=20, facecolor='#ff5050')
    ax_drawing.add_patch(arrow_bot)
    design_box = mpatches.Rectangle(xy=(-D.L/2, -D.H/2), width=D.L, height=D.H,
                                    alpha=0.5, edgecolor='k', linestyle='--')
    ax_drawing.add_patch(design_box)
    ax_drawing.annotate('design region', (0.5, 0.5), xytext=(0.0, 0.75),
                    xycoords='axes fraction',
                    textcoords='data',
                    size='small',
                    color='k',
                    horizontalalignment='center',
                    verticalalignment='center')
    ax_drawing.annotate('linear', (0.5, 0.5), xytext=(6, 1),
                    xycoords='axes fraction',
                    textcoords='data',
                    size='small',
                    color='k',
                    horizontalalignment='left',
                    verticalalignment='center')
    ax_drawing.annotate('nonlinear', (0.5, 0.5), xytext=(6, -y_dist - 1),
                    xycoords='axes fraction',
                    textcoords='data',
                    size='small',
                    color='k',
                    horizontalalignment='left',
                    verticalalignment='center')
    ax_drawing.annotate('X', (0.5, 0.5), xytext=(base_in-2.5, -y_dist-0.1),
                    xycoords='axes fraction',
                    textcoords='data',
                    size='large',
                    color='k',
                    fontweight='extra bold',
                    horizontalalignment='left',
                    verticalalignment='center')
    ax_drawing.get_xaxis().set_visible(False)
    ax_drawing.get_yaxis().set_visible(False)
    scalebar = AnchoredSizeBar(ax_drawing.transData,
                               5, '5 $\mu$m', 'lower left', 
                               pad=scale_bar_pad,
                               color='black',
                               frameon=False,
                               size_vertical=0.3,
                               fontproperties=fontprops)
    ax_drawing.add_artist(scalebar)
    ax_drawing.annotate('optimization definition', xy=(0.5, 0.5), xytext=(0.5, 0.94),
                    xycoords='axes fraction',
                    textcoords='axes fraction',
                    size='medium',
                    color='k',
                    horizontalalignment='center',
                    verticalalignment='center')


    # permittivity
    ax_eps = ax_top[1]
    im = ax_eps.pcolormesh(D.x_range, D.y_range, D.simulation.eps_r.T, cmap='Greys')
    ax_eps.set_xlabel('x position ($\mu$m)')
    ax_eps.set_ylabel('y position ($\mu$m)')
    # ax_eps.set_title('relative permittivity')
    cbar = plt.colorbar(im, ax=ax_eps)
    cbar.ax.set_title('$\epsilon_r$')

    ax_eps.get_xaxis().set_visible(False)
    ax_eps.get_yaxis().set_visible(False)
    scalebar = AnchoredSizeBar(ax_eps.transData,
                               5, '5 $\mu$m', 'lower left', 
                               pad=scale_bar_pad,
                               color='black',
                               frameon=False,
                               size_vertical=0.3,
                               fontproperties=fontprops)

    ax_eps.add_artist(scalebar)
    ax_eps.annotate('final structure', xy=(0.5, 0.5), xytext=(0.5, 0.94),
                    xycoords='axes fraction',
                    textcoords='axes fraction',
                    size='medium',
                    color='k',
                    horizontalalignment='center',
                    verticalalignment='center')

    # linear fields
    ax_lin = ax_mid[0]
    E_lin = np.abs(D.Ez.T)
    vmin = 3
    vmax = E_lin.max()/1.5
    im = ax_lin.pcolormesh(D.x_range, D.y_range, E_lin, cmap='inferno', norm=LogNorm(vmin=vmin, vmax=vmax))
    ax_lin.contour(D.x_range, D.y_range, D.simulation.eps_r.T, levels=2, linewidths=0.2, colors='w')
    ax_lin.set_xlabel('x position ($\mu$m)')
    ax_lin.set_ylabel('y position ($\mu$m)')
    # ax_lin.set_title('linear fields')
    cbar = plt.colorbar(im, ax=ax_lin)
    cbar.ax.set_title('$|E_z|$')
    # cbar.ax.tick_params(axis='x', direction='in', labeltop=True)
    ax_lin.annotate('linear fields', xy=(0.5, 0.5), xytext=(0.5, 0.94),
                    xycoords='axes fraction',
                    textcoords='axes fraction',
                    size='medium',
                    color='w',
                    horizontalalignment='center',
                    verticalalignment='center')

    ax_lin.get_xaxis().set_visible(False)
    ax_lin.get_yaxis().set_visible(False)
    scalebar = AnchoredSizeBar(ax_lin.transData,
                               5, '5 $\mu$m', 'lower left', 
                               pad=scale_bar_pad,
                               color='white',
                               frameon=False,
                               size_vertical=0.3,
                               fontproperties=fontprops)
    ax_lin.add_artist(scalebar)

    # nonlinear fields
    ax_nl = ax_mid[1]
    E_nl = np.abs(D.Ez_nl.T)
    vmin = 3
    # vmax = E_nl.max()    
    im = ax_nl.pcolormesh(D.x_range, D.y_range, E_nl, cmap='inferno', norm=LogNorm(vmin=vmin, vmax=vmax))
    ax_nl.contour(D.x_range, D.y_range, D.simulation.eps_r.T, levels=2, linewidths=0.2, colors='w')
    ax_nl.set_xlabel('x position ($\mu$m)')
    ax_nl.set_ylabel('y position ($\mu$m)')
    cbar = plt.colorbar(im, ax=ax_nl)
    cbar.ax.set_title('$|E_z|$')    
    ax_nl.annotate('nonlinear fields', xy=(0.5, 0.5), xytext=(0.5, 0.94),
                    xycoords='axes fraction',
                    textcoords='axes fraction',
                    size='medium',
                    color='w',
                    horizontalalignment='center',
                    verticalalignment='center')

    ax_nl.get_xaxis().set_visible(False)
    ax_nl.get_yaxis().set_visible(False)
    scalebar = AnchoredSizeBar(ax_nl.transData,
                               5, '5 $\mu$m', 'lower left', 
                               pad=scale_bar_pad,
                               color='white',
                               frameon=False,
                               size_vertical=0.3,
                               fontproperties=fontprops)
    ax_nl.add_artist(scalebar)


    # objective function
    ax_obj = ax_bot[0]
    obj_list = D.optimization.objfn_list
    iter_list = range(1, len(obj_list) + 1)
    ax_obj.plot(iter_list, obj_list)
    ax_obj.set_xlabel('iteration')
    ax_obj.set_ylabel('objective (max 1)')


    f0 = 3e8/D.lambda0
    freqs_scaled = [(f0 - f)/1e9 for f in D.freqs]
    objs = D.objs
    inset = inset_axes(ax_obj,
                    width="40%", # width = 30% of parent_bbox
                    height=0.5, # height : 1 inch
                    loc=7)
    inset.plot(freqs_scaled, objs, linewidth=1)
    inset.set_xlabel('$\Delta f$ $(GHz)$')
    inset.set_ylabel('objective')    
    set_axis_font(inset, 6)

    # power scan
    ax_power = ax_bot[1] 

    # ax_power.plot(D.powers, D.transmissions[0])
    # ax_power.set_xscale('log')
    # ax_power.set_xlabel('input power (W / $\mu$m)')
    # ax_power.set_ylabel('transmission')
    # ax_power.legend(('right', 'top'))

    apply_sublabels([ax_drawing, ax_eps, ax_lin, ax_nl, ax_power, ax_obj], invert_color_inds=[False, False, True, True, False, False])

    return f

############################################################################################################################################
############################################################################################################################################
############################################################################################################################################
############################################################################################################################################

def plot_three_port(D):

    eps_disp, design_region = three_port(D.L, D.H, D.w, D.l, D.spc, D.dl, D.NPML, D.eps_m)
    f, (ax_top, ax_bot) = plt.subplots(2, 2, figsize=(7, 5), constrained_layout=True)

    # draw structure
    ax_drawing = ax_top[0]
    im = ax_drawing.pcolormesh(D.x_range, D.y_range, eps_disp.T, cmap='Greys')
    ax_drawing.set_xlabel('x position ($\mu$m)')
    ax_drawing.set_ylabel('y position ($\mu$m)')
    y_dist = 1.6
    base_in = 7
    tip_in = 3
    y_shift = 0.01
    arrow_in = mpatches.FancyArrowPatch((-base_in, +y_shift), (-tip_in, y_shift),
                                     mutation_scale=20, facecolor='#cc99ff')
    ax_drawing.add_patch(arrow_in)
    arrow_top = mpatches.FancyArrowPatch((tip_in, y_dist+0.1+y_shift), (base_in, y_dist+0.1+y_shift),
                                     mutation_scale=20, facecolor='#3366ff',
                                     edgecolor='k')
    ax_drawing.add_patch(arrow_top)
    arrow_bot = mpatches.FancyArrowPatch((tip_in, -y_dist+y_shift), (base_in, -y_dist+y_shift),
                                     mutation_scale=20, facecolor='#ff5050')
    ax_drawing.add_patch(arrow_bot)

    design_box = mpatches.Rectangle(xy=(-D.L/2, -D.H/2), width=D.L, height=D.H,
                                    alpha=0.5,
                                    edgecolor='k',
                                    linestyle='--')
    ax_drawing.add_patch(design_box)

    ax_drawing.annotate('design\nregion', (0.5, 0.5), xytext=(0.0, 0.0),
                    xycoords='axes fraction',
                    textcoords='data',
                    size='small',
                    color='k',
                    horizontalalignment='center',
                    verticalalignment='center')
    ax_drawing.annotate('linear', (0, 0), xytext=(3.5, 0.8),
                    xycoords='axes fraction',
                    textcoords='data',
                    size='small',
                    color='k',
                    horizontalalignment='left',
                    verticalalignment='center')
    ax_drawing.annotate('nonlinear', (0, 0), xytext=(3.5, -2.4),
                    xycoords='axes fraction',
                    textcoords='data',
                    size='small',
                    color='k',
                    horizontalalignment='left',
                    verticalalignment='center')

    ax_drawing.get_xaxis().set_visible(False)
    ax_drawing.get_yaxis().set_visible(False)
    scalebar = AnchoredSizeBar(ax_drawing.transData,
                               5, '5 $\mu$m', 'lower left', 
                               pad=scale_bar_pad,
                               color='black',
                               frameon=False,
                               size_vertical=0.3,
                               fontproperties=fontprops)
    ax_drawing.add_artist(scalebar)
    ax_drawing.annotate('optimization definition', xy=(0.5, 0.5), xytext=(0.5, 0.94),
                    xycoords='axes fraction',
                    textcoords='axes fraction',
                    size='medium',
                    color='k',
                    horizontalalignment='center',
                    verticalalignment='center')


    # permittivity
    ax_eps = ax_top[1]
    im = ax_eps.pcolormesh(D.x_range, D.y_range, D.simulation.eps_r.T, cmap='Greys')
    ax_eps.set_xlabel('x position ($\mu$m)')
    ax_eps.set_ylabel('y position ($\mu$m)')
    # ax_eps.set_title('relative permittivity')
    cbar = plt.colorbar(im, ax=ax_eps)
    cbar.ax.set_title('$\epsilon_r$')

    ax_eps.get_xaxis().set_visible(False)
    ax_eps.get_yaxis().set_visible(False)
    scalebar = AnchoredSizeBar(ax_eps.transData,
                               5, '5 $\mu$m', 'lower left', 
                               pad=scale_bar_pad,
                               color='black',
                               frameon=False,
                               size_vertical=0.3,
                               fontproperties=fontprops)

    ax_eps.add_artist(scalebar)
    ax_eps.annotate('final structure', xy=(0.5, 0.5), xytext=(0.5, 0.94),
                    xycoords='axes fraction',
                    textcoords='axes fraction',
                    size='medium',
                    color='k',
                    horizontalalignment='center',
                    verticalalignment='center')

    # linear fields
    ax_lin = ax_bot[0]
    E_lin = np.abs(D.Ez.T)
    vmin = 3
    vmax = E_lin.max()
    im = ax_lin.pcolormesh(D.x_range, D.y_range, E_lin, cmap='inferno', norm=LogNorm(vmin=vmin, vmax=vmax))
    ax_lin.contour(D.x_range, D.y_range, D.simulation.eps_r.T, levels=2, linewidths=0.2, colors='w')
    ax_lin.set_xlabel('x position ($\mu$m)')
    ax_lin.set_ylabel('y position ($\mu$m)')
    # ax_lin.set_title('linear fields')
    cbar = plt.colorbar(im, ax=ax_lin)
    cbar.ax.set_title('$|E_z|$')
    # cbar.ax.tick_params(axis='x', direction='in', labeltop=True)
    ax_lin.annotate('linear fields', xy=(0.5, 0.5), xytext=(0.5, 0.94),
                    xycoords='axes fraction',
                    textcoords='axes fraction',
                    size='medium',
                    color='w',
                    horizontalalignment='center',
                    verticalalignment='center')

    ax_lin.get_xaxis().set_visible(False)
    ax_lin.get_yaxis().set_visible(False)
    scalebar = AnchoredSizeBar(ax_lin.transData,
                               5, '5 $\mu$m', 'lower left', 
                               pad=scale_bar_pad,
                               color='white',
                               frameon=False,
                               size_vertical=0.3,
                               fontproperties=fontprops)
    ax_lin.add_artist(scalebar)

    # nonlinear fields
    ax_nl = ax_bot[1]
    E_nl = np.abs(D.Ez_nl.T)
    vmin = 3
    vmax = E_nl.max()    
    im = ax_nl.pcolormesh(D.x_range, D.y_range, E_nl, cmap='inferno', norm=LogNorm(vmin=vmin, vmax=vmax))
    ax_nl.contour(D.x_range, D.y_range, D.simulation.eps_r.T, levels=2, linewidths=0.2, colors='w')
    ax_nl.set_xlabel('x position ($\mu$m)')
    ax_nl.set_ylabel('y position ($\mu$m)')
    cbar = plt.colorbar(im, ax=ax_nl)
    cbar.ax.set_title('$|E_z|$')    
    ax_nl.annotate('nonlinear fields', xy=(0.5, 0.5), xytext=(0.5, 0.94),
                    xycoords='axes fraction',
                    textcoords='axes fraction',
                    size='medium',
                    color='w',
                    horizontalalignment='center',
                    verticalalignment='center')

    ax_nl.get_xaxis().set_visible(False)
    ax_nl.get_yaxis().set_visible(False)
    scalebar = AnchoredSizeBar(ax_nl.transData,
                               5, '5 $\mu$m', 'lower left', 
                               pad=scale_bar_pad,
                               color='white',
                               frameon=False,
                               size_vertical=0.3,
                               fontproperties=fontprops)
    ax_nl.add_artist(scalebar)

    apply_sublabels([ax_drawing, ax_eps, ax_lin, ax_nl], invert_color_inds=[False, False, True, True])

    return f


############################################################################################################################################
############################################################################################################################################
############################################################################################################################################
############################################################################################################################################

def plot_ortho_port(D):

    max_shift = np.max(D.simulation.compute_index_shift())

    print(np.sum(D.simulation.eps_r[1,:]>1))
    print(np.sum(D.simulation.eps_r[:,1]>1))
    print(np.sum(D.simulation.eps_r[:,-1]>1))

    eps_disp, design_region = ortho_port(D.L, D.L2, D.H, D.H2, D.w, D.l, D.dl, D.NPML, D.eps_m)
    f, (ax_top, ax_mid, ax_bot) = plt.subplots(3, 2, figsize=(7, 5), constrained_layout=True)

    eps_disp = np.flipud(eps_disp.T)

    # draw structure
    ax_drawing = ax_top[0]
    im = ax_drawing.pcolormesh(D.x_range, D.y_range, eps_disp, cmap='Greys')
    ax_drawing.set_xlabel('x position ($\mu$m)')
    ax_drawing.set_ylabel('y position ($\mu$m)')
    y_dist = 1.6
    base_in = 7
    tip_in = 3
    y_shift = 0.01
    arrow_in = mpatches.FancyArrowPatch((-base_in, +y_shift), (-tip_in, y_shift),
                                     mutation_scale=20, facecolor='#cc99ff')
    ax_drawing.add_patch(arrow_in)
    arrow_top = mpatches.FancyArrowPatch((tip_in, y_dist+0.1+y_shift), (base_in, y_dist+0.1+y_shift),
                                     mutation_scale=20, facecolor='#3366ff',
                                     edgecolor='k')
    ax_drawing.add_patch(arrow_top)
    arrow_bot = mpatches.FancyArrowPatch((tip_in, -y_dist+y_shift), (base_in, -y_dist+y_shift),
                                     mutation_scale=20, facecolor='#ff5050')
    ax_drawing.add_patch(arrow_bot)

    design_box = mpatches.Rectangle(xy=(-D.L/2, -D.H/2), width=D.L, height=D.H,
                                    alpha=0.5,
                                    edgecolor='k',
                                    linestyle='--')
    ax_drawing.add_patch(design_box)

    ax_drawing.annotate('design\nregion', (0.5, 0.5), xytext=(0.0, 0.0),
                    xycoords='axes fraction',
                    textcoords='data',
                    size='small',
                    color='k',
                    horizontalalignment='center',
                    verticalalignment='center')
    ax_drawing.annotate('linear', (0, 0), xytext=(3.5, 0.8),
                    xycoords='axes fraction',
                    textcoords='data',
                    size='small',
                    color='k',
                    horizontalalignment='left',
                    verticalalignment='center')
    ax_drawing.annotate('nonlinear', (0, 0), xytext=(3.5, -2.4),
                    xycoords='axes fraction',
                    textcoords='data',
                    size='small',
                    color='k',
                    horizontalalignment='left',
                    verticalalignment='center')

    ax_drawing.get_xaxis().set_visible(False)
    ax_drawing.get_yaxis().set_visible(False)
    scalebar = AnchoredSizeBar(ax_drawing.transData,
                               5, '5 $\mu$m', 'lower left', 
                               pad=scale_bar_pad,
                               color='black',
                               frameon=False,
                               size_vertical=0.3,
                               fontproperties=fontprops)
    ax_drawing.add_artist(scalebar)
    ax_drawing.annotate('optimization definition', xy=(0.5, 0.5), xytext=(0.5, 0.94),
                    xycoords='axes fraction',
                    textcoords='axes fraction',
                    size='medium',
                    color='k',
                    horizontalalignment='center',
                    verticalalignment='center')


    # permittivity
    ax_eps = ax_top[1]
    eps_final = np.flipud(D.simulation.eps_r.T)
    im = ax_eps.pcolormesh(D.x_range, D.y_range, eps_final, cmap='Greys')
    ax_eps.set_xlabel('x position ($\mu$m)')
    ax_eps.set_ylabel('y position ($\mu$m)')
    # ax_eps.set_title('relative permittivity')
    cbar = plt.colorbar(im, ax=ax_eps)
    cbar.ax.set_title('$\epsilon_r$')

    ax_eps.get_xaxis().set_visible(False)
    ax_eps.get_yaxis().set_visible(False)
    scalebar = AnchoredSizeBar(ax_eps.transData,
                               5, '5 $\mu$m', 'lower left', 
                               pad=scale_bar_pad,
                               color='black',
                               frameon=False,
                               size_vertical=0.3,
                               fontproperties=fontprops)

    ax_eps.add_artist(scalebar)
    ax_eps.annotate('final structure', xy=(0.5, 0.5), xytext=(0.5, 0.94),
                    xycoords='axes fraction',
                    textcoords='axes fraction',
                    size='medium',
                    color='k',
                    horizontalalignment='center',
                    verticalalignment='center')

    # linear fields
    ax_lin = ax_mid[0]
    E_lin = np.flipud(np.abs(D.Ez.T))
    vmin = 1
    vmax = E_lin.max()/1.5
    im = ax_lin.pcolormesh(D.x_range, D.y_range, E_lin, cmap='inferno', norm=LogNorm(vmin=vmin, vmax=vmax))
    ax_lin.contour(D.x_range, D.y_range, eps_final, levels=2, linewidths=0.2, colors='w')
    ax_lin.set_xlabel('x position ($\mu$m)')
    ax_lin.set_ylabel('y position ($\mu$m)')
    # ax_lin.set_title('linear fields')
    cbar = plt.colorbar(im, ax=ax_lin)
    cbar.ax.set_title('$|E_z|$')
    # cbar.ax.tick_params(axis='x', direction='in', labeltop=True)
    ax_lin.annotate('linear fields', xy=(0.5, 0.5), xytext=(0.5, 0.94),
                    xycoords='axes fraction',
                    textcoords='axes fraction',
                    size='medium',
                    color='w',
                    horizontalalignment='center',
                    verticalalignment='center')

    ax_lin.get_xaxis().set_visible(False)
    ax_lin.get_yaxis().set_visible(False)
    scalebar = AnchoredSizeBar(ax_lin.transData,
                               5, '5 $\mu$m', 'lower left', 
                               pad=scale_bar_pad,
                               color='white',
                               frameon=False,
                               size_vertical=0.3,
                               fontproperties=fontprops)
    ax_lin.add_artist(scalebar)

    # nonlinear fields
    ax_nl = ax_mid[1]
    E_nl = np.flipud(np.abs(D.Ez_nl.T))
    vmin = 1
    im = ax_nl.pcolormesh(D.x_range, D.y_range, E_nl, cmap='inferno', norm=LogNorm(vmin=vmin, vmax=vmax))
    ax_nl.contour(D.x_range, D.y_range, eps_final, levels=2, linewidths=0.2, colors='w')
    ax_nl.set_xlabel('x position ($\mu$m)')
    ax_nl.set_ylabel('y position ($\mu$m)')
    cbar = plt.colorbar(im, ax=ax_nl)
    cbar.ax.set_title('$|E_z|$')    
    ax_nl.annotate('nonlinear fields', xy=(0.5, 0.5), xytext=(0.5, 0.94),
                    xycoords='axes fraction',
                    textcoords='axes fraction',
                    size='medium',
                    color='w',
                    horizontalalignment='center',
                    verticalalignment='center')

    ax_nl.get_xaxis().set_visible(False)
    ax_nl.get_yaxis().set_visible(False)
    scalebar = AnchoredSizeBar(ax_nl.transData,
                               5, '5 $\mu$m', 'lower left', 
                               pad=scale_bar_pad,
                               color='white',
                               frameon=False,
                               size_vertical=0.3,
                               fontproperties=fontprops)
    ax_nl.add_artist(scalebar)

    # objective function
    ax_obj = ax_bot[0]
    obj_list = D.optimization.objfn_list
    iter_list = range(1, len(obj_list) + 1)
    ax_obj.plot(iter_list, obj_list)
    ax_obj.set_xlabel('iteration')
    ax_obj.set_ylabel('objective (max 1)')


    # f0 = 3e8/D.lambda0
    # freqs_scaled = [(f0 - f)/1e9 for f in D.freqs]
    # objs = D.objs
    # inset = inset_axes(ax_obj,
    #                 width="40%", # width = 30% of parent_bbox
    #                 height=0.5, # height : 1 inch
    #                 loc=7)
    # inset.plot(freqs_scaled, objs, linewidth=1)
    # inset.set_xlabel('$\Delta f$ $(GHz)$')
    # inset.set_ylabel('objective')    
    # set_axis_font(inset, 6)

    # power scan
    ax_power = ax_bot[1] 

    for i in range(2):
        ax_power.plot(D.powers, D.transmissions[i])
    ax_power.set_xscale('log')
    ax_power.set_xlabel('input power (W / $\mu$m)')
    ax_power.set_ylabel('transmission')
    ax_power.legend(('right', 'top'), loc='best')

    apply_sublabels([ax_drawing, ax_eps, ax_lin, ax_nl, ax_power, ax_obj], invert_color_inds=[False, False, True, True, False, False])

    return f


############################################################################################################################################
############################################################################################################################################
############################################################################################################################################
############################################################################################################################################


def apply_sublabels(axs, invert_color_inds, x=19, y=-5, size='large', ha='right', va='top', prefix='(', postfix=')'):
    # axs = list of axes
    # invert_color_ind = list of booleans (True to make sublabels white, else False)
    for n, ax in enumerate(axs):
        if invert_color_inds[n]:
            color='w'
        else:
            color='k'
        ax.annotate(prefix + ascii_lowercase[n] + postfix,
                    xy=(0, 1),
                    xytext=(x, y),
                    xycoords='axes fraction',
                    textcoords='offset points',
                    size=size,
                    color=color,
                    horizontalalignment=ha,
                    verticalalignment=va)

def load_device(fname):
    """ Loads the pickled Device object """
    D_dict = pickle.load(open(fname, "rb"))
    D = namedtuple('Device', D_dict.keys())(*D_dict.values())
    return D

if __name__ == '__main__':

    fname2 = "data/figs/devices/2_port.p"
    D2 = load_device(fname2)

    fig = plot_Device(D2)
    plt.show()

    # fname3 = "data/figs/devices/3_port.p"
    # D3 = load_device(fname3)
    # fig = plot_Device(D3)
    # plt.show()

    fnameT = "data/figs/devices/T_port.p"
    DT = load_device(fnameT)
    fig = plot_Device(DT)
    # plt.savefig('data/test.png', dpi=400)
    plt.show()