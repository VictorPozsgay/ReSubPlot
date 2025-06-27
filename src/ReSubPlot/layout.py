"""This module has all the functions that extract information from an
existing Figure object."""

#pylint: disable=line-too-long
#pylint: disable=trailing-whitespace
#pylint: disable=invalid-name

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.collections as mcoll
from matplotlib.collections import LineCollection
from matplotlib.collections import PathCollection
import matplotlib.ticker as ticker

def recover_figsize(old_fig):
    """ Function takes a figure object and extracts size in inches
    
    Parameters
    ----------
    old_fig : Figure
        original figure 

    Returns
    -------
    size of the figure in inches
    """
    return old_fig.get_size_inches()

def recover_axis_position(old_ax, new_ax):
    """ Function takes an axis object and
    recovers x and y axis position

    Parameters
    ----------
    old_ax : matplotlib.axes._axes.Axes
        Axis of the original figure
    new_ax : matplotlib.axes._axes.Axes
        Axis of the new figure

    Returns
    -------
    x and y axis positions
    """
    new_ax.set_position(old_ax.get_position())

def sharing_axis(new_ax_og, old_fig, old_ax):
    """ Function takes an axis object and
    finds how to best create the new axis

    Parameters
    ----------
    new_ax_og : matplotlib.axes._axes.Axes
        Axis of the new figure
    old_fig : Figure
        original figure 
    old_ax : matplotlib.axes._axes.Axes
        Axis of the original figure
        
    Returns
    -------
    new_ax : matplotlib.axes._axes.Axes
        Axis of the new figure
    """
    # when looping through axis, finds out whether the current axis is the
    # same as the first axis of the list
    if old_ax == old_fig.axes[0]:
        new_ax = new_ax_og
        # if not, figures whether they share x or y axis and recovers the position
    else:
        if old_fig.axes[0].get_shared_x_axes().joined(old_fig.axes[0], old_ax):
            new_ax = new_ax_og.twinx()
        if old_fig.axes[0].get_shared_y_axes().joined(old_fig.axes[0], old_ax):
            new_ax = new_ax_og.twiny()
        # else:
        #     new_ax = new_ax_og
        # recover_axis_position(old_ax, new_ax)
    # new_ax.set_position(new_ax_og.get_position())
    return new_ax

def recover_Line2D(old_ax, new_ax):
    """ Function takes an axis and extracts all 2d lines, including axlines

    Parameters
    ----------
    old_ax : matplotlib.axes._axes.Axes
        Axis of the original figure
    new_ax : matplotlib.axes._axes.Axes
        Axis of the new figure
    """
    for line in old_ax.get_lines():
        y_data = np.array(line.get_ydata())  # Convert to numpy array if it's not already
        x_data = np.array(line.get_xdata())  # Convert to numpy array if it's not already
        # Check if the line is a horizontal line (constant y-value)
        if y_data.size == 2:  
            if y_data[0] == y_data[-1]: # If it's a horizontal line (constant y-value)
                y_value = y_data[0]
                
                # Recover the axhline using axhline in new_ax
                new_ax.axhline(
                    y=y_value,
                    color=line.get_color(),
                    linestyle=line.get_linestyle(),
                    linewidth=line.get_linewidth(),
                    label=line.get_label()  # If you want to recover the label as well
                )
            elif x_data[0] == x_data[-1]: # If it's a vertical line (constant x-value)
                x_value = x_data[0]

                # Recover the axhline using axhline in new_ax
                new_ax.axvline(
                    x=x_value,
                    color=line.get_color(),
                    linestyle=line.get_linestyle(),
                    linewidth=line.get_linewidth(),
                    label=line.get_label()  # If you want to recover the label as well
                )
            # recovers any other Line2D
            else:
                new_ax.plot(
                    line.get_xdata(), 
                    line.get_ydata(), 
                    label=line.get_label(),
                    color=line.get_color(),
                    linestyle=line.get_linestyle()
                )
        # recovers any other Line2D
        else:
            new_ax.plot(
                line.get_xdata(), 
                line.get_ydata(), 
                label=line.get_label(),
                color=line.get_color(),
                linestyle=line.get_linestyle()
            )

def recover_hlines_vlines(old_ax, new_ax):
    """ Function takes an axis and extracts all hlines() and vlines()

    Parameters
    ----------
    old_ax : matplotlib.axes._axes.Axes
        Axis of the original figure
    new_ax : matplotlib.axes._axes.Axes
        Axis of the new figure
    """
    # Original Axes and its LineCollections
    collections = [c for c in old_ax.collections if isinstance(c, LineCollection)]
    
    xmin, xmax = old_ax.get_xlim()
    ymin, ymax = old_ax.get_ylim()

    for coll in collections:
        segments = coll.get_segments()
        
        # Visual properties
        colors = coll.get_colors()
        linewidths = coll.get_linewidths()
        linestyles = coll.get_linestyles()
        alpha = coll.get_alpha()
        label = coll.get_label()

        # Handle segment by segment
        for i, seg in enumerate(segments):
            (x0, y0), (x1, y1) = seg
            color = colors[i % len(colors)] if len(colors) > 0 else 'black'
            lw = linewidths[i % len(linewidths)] if len(linewidths) > 0 else 1.0
            ls = linestyles[i % len(linestyles)] if len(linestyles) > 0 else 'solid'
            show_label = label if i == 0 else '_nolegend_'  # avoid label duplication

            if (x0 == x1) and (y0 == ymin) and (y1 == ymax):
                # Full vertical line: Use axvline for auto y-extent
                new_ax.axvline(
                    x=x0, color=color, linestyle=ls,
                    linewidth=lw, alpha=alpha, label=show_label
                )
            elif (y0 == y1) and (x0 == xmin) and (x1 == xmax):
                # Full horizontal line: Use axhline for auto y-extent
                new_ax.axhline(
                    x=x0, color=color, linestyle=ls,
                    linewidth=lw, alpha=alpha, label=show_label
                )
            else:
                # Horizontal (or diagonal): Keep as LineCollection
                new_coll = LineCollection(
                    [seg], colors=[color], linewidths=[lw],
                    linestyles=[ls], alpha=alpha, label=show_label
                )
                new_ax.add_collection(new_coll)

def recover_errorbars(old_ax, new_ax):
    """ Function takes an axis and extracts all hlines() and vlines()

    Parameters
    ----------
    old_ax : matplotlib.axes._axes.Axes
        Axis of the original figure
    new_ax : matplotlib.axes._axes.Axes
        Axis of the new figure
    """
    cont = [c.lines[-1] for c in old_ax.containers if hasattr(c, 'lines')]
    cont = [c for cc in cont for c in cc]

    for coll in cont:
        segments = coll.get_segments()
        
        # Visual properties
        colors = coll.get_colors()
        linewidths = coll.get_linewidths()
        linestyles = coll.get_linestyles()
        alpha = coll.get_alpha()
        label = coll.get_label()

        # Handle segment by segment
        for i, seg in enumerate(segments):
            (x0, y0), (x1, y1) = seg
            color = colors[i % len(colors)] if len(colors) > 0 else 'black'
            lw = linewidths[i % len(linewidths)] if len(linewidths) > 0 else 1.0
            ls = linestyles[i % len(linestyles)] if len(linestyles) > 0 else 'solid'
            show_label = label if i == 0 else '_nolegend_'  # avoid label duplication

            if x0 == x1:
                # Vertical: Use axvline for auto y-extent
                new_ax.vlines(
                    x=x0, ymin=y0, ymax=y1, color=color, linestyle=ls,
                    linewidth=lw, alpha=alpha, label=show_label
                )
            else:
                # Horizontal (or diagonal): Keep as LineCollection
                new_coll = LineCollection(
                    [seg], colors=[color], linewidths=[lw],
                    linestyles=[ls], alpha=alpha, label=show_label
                )
                new_ax.add_collection(new_coll)

def recover_fill_between(old_ax, new_ax):
    """ Function takes an axis and extracts all fill_between

    Parameters
    ----------
    old_ax : matplotlib.axes._axes.Axes
        Axis of the original figure
    new_ax : matplotlib.axes._axes.Axes
        Axis of the new figure
    """
    for poly in old_ax.collections:
        if isinstance(poly, mcoll.PolyCollection):
            # Each PolyCollection could have multiple polygons
            for path in poly.get_paths():
                verts = path.vertices
                x_pre = verts[:, 0]
                x = x_pre[1:int(len(x_pre)/2)]
                y = verts[:, 1]
                y1 = y[1:int(len(y)/2)]
                y2 = y[int(len(y)/2)+1:-1][::-1]
                new_ax.fill_between(
                    x, y1=y1, y2=y2, 
                    color=poly.get_facecolor()[0], 
                    alpha=poly.get_alpha()
                )

def recover_scatter(old_ax, new_ax):
    """ Function takes an axis and extracts all scatter plot data

    Parameters
    ----------
    old_ax : matplotlib.axes._axes.Axes
        Axis of the original figure
    new_ax : matplotlib.axes._axes.Axes
        Axis of the new figure
    """
    # Get original axis and scatter collections
    scatters = [c for c in old_ax.collections if isinstance(c, PathCollection)]

    for scatter in scatters:
        new_ax.scatter(
            scatter.get_offsets()[:, 0], scatter.get_offsets()[:, 1],
            s=scatter.get_sizes(),
            c=scatter.get_facecolors() if len(scatter.get_facecolors()) > 0 else None,
            edgecolors=scatter.get_edgecolors() if len(scatter.get_edgecolors()) > 0 else None,
            alpha=scatter.get_alpha(),
            label=scatter.get_label() if scatter.get_label() != '_nolegend_' else None  # Only keep valid labels
        )

def recover_barplot(old_ax, new_ax):
    """ Function takes an axis and extracts all bar plot data

    Parameters
    ----------
    old_ax : matplotlib.axes._axes.Axes
        Axis of the original figure
    new_ax : matplotlib.axes._axes.Axes
        Axis of the new figure
    """
    bars = [patch for patch in old_ax.patches if isinstance(patch, plt.Rectangle)]
    bars = [b for b in bars if b.get_y() != 0 or b.get_height() != old_ax.get_ylim()[1]]

    bar_data = []
    for b in bars:
        edge = b.get_edgecolor()
        if isinstance(edge, (tuple, list)) and len(edge) == 4 and edge[-1] == 0.0:
            edge = 'none'
        bar_data.append({
            "x": b.get_x(),
            "y": b.get_y(),
            "width": b.get_width(),
            "height": b.get_height(),
            "facecolor": b.get_facecolor(),
            "edgecolor": edge,
            "linewidth": b.get_linewidth(),
            "linestyle": b.get_linestyle(),
            "alpha": b.get_alpha(),
            "original_bar": b
        })

    handles, labels = old_ax.get_legend_handles_labels()

    new_bars = []
    # Replot all bars WITHOUT labels
    for b in bar_data:
        bar = new_ax.bar(
            b["x"],
            b["height"],
            width=b["width"],
            color=b["facecolor"],
            edgecolor=b["edgecolor"],
            linewidth=b["linewidth"],
            linestyle=b["linestyle"],
            alpha=b["alpha"],
            align='edge'
        )[0]
        new_bars.append(bar)

    # Now assign labels to a subset of bars for the legend:
    # Match old handles to new bars by color or position
    # Here we do a simple color-based matching:
    for handle, label in zip(handles, labels):
        # Find first new bar matching handle color and assign label
        target_fc = handle.get_facecolor() if hasattr(handle, 'get_facecolor') else None
        for bar in new_bars:
            if np.allclose(bar.get_facecolor(), target_fc):
                bar.set_label(label)
                break

def recover_axis_formatting(old_ax, new_ax):
    """ Function takes an axis and recovers axis formatting

    Parameters
    ----------
    old_ax : matplotlib.axes._axes.Axes
        Axis of the original figure
    new_ax : matplotlib.axes._axes.Axes
        Axis of the new figure
    """
    # Recover axis labels and title from the original axes
    new_ax.set_xlabel(old_ax.get_xlabel())
    new_ax.set_ylabel(old_ax.get_ylabel())
    new_ax.set_title(old_ax.get_title())

    # Recover tick labels (if any custom ticks were used)
    new_ax.set_xticks(old_ax.get_xticks())
    # new_ax.set_yticks(old_ax.get_yticks())
    new_ax.set_xticklabels(old_ax.get_xticklabels())
    # new_ax.set_yticklabels(old_ax.get_yticklabels())

    # Recover x and y limits from the original axes
    new_ax.set_xlim(old_ax.get_xlim())
    new_ax.set_ylim(old_ax.get_ylim())

def recover_legend(old_ax, new_ax):
    """ Function takes an axis and recovers legend

    Parameters
    ----------
    old_ax : matplotlib.axes._axes.Axes
        Axis of the original figure
    new_ax : matplotlib.axes._axes.Axes
        Axis of the new figure
    """
    new_ax.legend(*old_ax.get_legend_handles_labels())

def print_into_row_subplots(temp_fig_list, new_fig, pad):
    """ Function takes a list of figure objects and 
    prints them into subplots
    
    Parameters
    ----------
    temp_fig_list : list of Figure
        List of original figures to be plotted in a subplots()
        in the format of the list
    new_fig : Figure
        New figure where the subplots will be created
    pad : float
        padding between subplots, suggest 0.05

    Returns
    -------
    tens : list
        list in the subplot shape that indicates the numbering of axes 
        for each subplot
    """
    num_ax = 0
    tens = []
    (nrows, ncols) = np.array(temp_fig_list).shape
    for i,m in enumerate(temp_fig_list):
        mat = []
        for j,f in enumerate(m):
            vec=[]
            ax = new_fig.add_subplot(nrows, ncols, i*ncols+j+1)
            # print(nrows, ncols, i*ncols+j+1, i*ncols+j+1)
            plot_same_new_figure(f, ax)
            num_new_ax = len(new_fig.axes)-num_ax
            for n in range(num_ax,num_ax+num_new_ax):
                vec.append(n)
                new_fig.axes[n].set_position([(j+pad)/ncols, (i+pad)/nrows, (1-2*pad)/ncols, (1-2*pad)/nrows])
            num_ax = len(new_fig.axes)
            mat.append(vec)
        tens.append(mat)
        # !!!!!!!!!!!!!!! NEED THIS !!!!!!!!!!!!!!!
    tens = tens[::-1]

    return tens

def create_figure(mat_fig, list_sites, pad):
    """ Function takes a list of figure objects and 
    prints them into subplots
    
    Parameters
    ----------
    mat_fig : list of Figure
        List of original figures to be plotted in a subplots()
        in the format of the list
        It has to be an n*m list [[fig1, ..., fign], [], ..., []]
    list_sites : list
        List of sites, 1 site per column
        will be used to label each column
    pad : float
        padding between subplots, suggest 0.03

    Returns
    -------
    fig : Figure
        figure with subplots
    tens : list
        list in the subplot shape that indicates the numbering of axes 
        for each subplot
    """
    temp_fig_list = np.array(mat_fig).reshape(-1,len(list_sites))
    # !!!!!!!!!!!!!!! I DO NOT UNDERSTAND !!!!!!!!!!!!!!!
    # For some reason, the rows are swapped so I need to unswap here
    # but it complicates a few other things, especially the definition of 'tens' 
    temp_fig_list = temp_fig_list[::-1]
    (_, ncols) = temp_fig_list.shape
    fig = plt.figure(figsize=(ncols*np.max([f[0].get_size_inches()[0] for f in temp_fig_list]),
                              np.sum([f[0].get_size_inches()[1] for f in temp_fig_list])))
    tens = print_into_row_subplots(temp_fig_list, fig, pad)
    # fig.tight_layout()

    return fig, tens

def legends_only_last_subplot(fig, tens):
    """ Function makes sure legend is only plotted on the 
    last subplot of each row
    
    Parameters
    ----------
    fig : Figure
        figure with subplots
    tens : list
        list in the subplot shape that indicates the numbering of axes 
        for each subplot

    Returns
    -------
    fig : Figure
        figure with subplots
    """
    for mat in tens:
        flat_mat = [j for i in mat for j in i]
        handles, labels = [], []
        for i,ax in enumerate(fig.axes[flat_mat[0]:flat_mat[-1]+1]):
            if i+flat_mat[0] in mat[-1]:
                h,l=ax.get_legend_handles_labels()
                handles+=h
                labels+=l
                if i+flat_mat[0]==mat[-1][-1]:
                    ax.legend(handles, labels)
                else:
                    if ax.get_legend() is not None:
                        ax.get_legend().remove()
            else:
                if ax.get_legend() is not None:
                    ax.get_legend().remove()
    # fig.tight_layout()

    return fig

def labels_only_last_subplot(fig, tens):
    """ Function makes sure labels are only plotted on the 
    first and last subplot of each row depending on their 
    left/right y position
    
    Parameters
    ----------
    fig : Figure
        figure with subplots
    tens : list
        list in the subplot shape that indicates the numbering of axes 
        for each subplot

    Returns
    -------
    fig : Figure
        figure with subplots
    """
    for mat in tens:
        for row,i in enumerate(mat):
            for num_ax,j in enumerate(i):
                if row>0 and num_ax==0:
                    fig.axes[j].set_ylabel('')
                    fig.axes[j].set_yticklabels('')
                if row<len(mat)-1 and num_ax==1:
                    fig.axes[j].set_ylabel('')
                    fig.axes[j].set_yticklabels('')
    # fig.tight_layout()

    return fig

def set_common_ylims(fig, tens):
    """ Function makes sure that all y limits are common
    across a row of subplots, even for twinx axes
    
    Parameters
    ----------
    fig : Figure
        figure with subplots
    tens : list
        list in the subplot shape that indicates the numbering of axes 
        for each subplot

    Returns
    -------
    fig : Figure
        figure with subplots
    """
    for mat in tens:
        for j in range(np.array(mat).shape[1]):
            y_min_all = np.min([lim for i,lim in enumerate(list((np.array([list(ax.get_ylim()) for ax in fig.axes]).T)[0])) if i in [m[j] for m in mat]])
            y_max_all = np.max([lim for i,lim in enumerate(list((np.array([list(ax.get_ylim()) for ax in fig.axes]).T)[1])) if i in [m[j] for m in mat]])
            for m in mat:
                fig.axes[m[j]].set_ylim(y_min_all,y_max_all)
    # fig.tight_layout()

    return fig

def set_common_xlims(fig, tens, sharex):
    """ Function makes sure that all x limits are common
    across a row, a col, or both of subplots, even for twinx axes
    
    Parameters
    ----------
    fig : Figure
        figure with subplots
    tens : list
        list in the subplot shape that indicates the numbering of axes 
        for each subplot
    sharex : bool or {'none', 'all', 'row', 'col'}, optional, default: False
        Controls sharing of properties among x axes:
        True or 'all': x-axis will be shared among all subplots.
        False or 'none': each subplot x-axis will be independent.
        'row': each subplot row will share an x-axis.
        'col': each subplot column will share an x-axis.

    Returns
    -------
    fig : Figure
        figure with subplots
    """
    if sharex == 'row':
        fig = sharex_rows(fig, tens)
    elif sharex == 'col':
        fig = sharex_cols(fig, tens)
    elif (sharex == True) or (sharex == 'all'):
        fig = sharex_rows(fig, tens)
        fig = sharex_cols(fig, tens)
    else:
        pass

    return fig

def sharex_rows(fig, tens):
    """ Function makes sure that all x limits are common
    across a row of subplots, even for twinx axes
    
    Parameters
    ----------
    fig : Figure
        figure with subplots
    tens : list
        list in the subplot shape that indicates the numbering of axes 
        for each subplot

    Returns
    -------
    fig : Figure
        figure with subplots
    """
    lims = [[fig.axes[r].get_xlim() for rr in row for r in rr] for row in tens]
    xmin = [np.min([i[0] for i in row]) for row in lims]
    xmax = [np.max([i[1] for i in row]) for row in lims]
    for nrow,row in enumerate(tens):
        for i in [r for rr in row for r in rr]:
            ax = fig.axes[i]
            ax.set_xlim(xmin[nrow], xmax[nrow])
            ax.xaxis.set_major_locator(ticker.AutoLocator())
            ax.xaxis.set_major_formatter(ticker.ScalarFormatter())

    return fig

def sharex_cols(fig, tens):
    """ Function makes sure that all x limits are common
    across a col of subplots, even for twinx axes
    
    Parameters
    ----------
    fig : Figure
        figure with subplots
    tens : list
        list in the subplot shape that indicates the numbering of axes 
        for each subplot

    Returns
    -------
    fig : Figure
        figure with subplots
    """
    tens_transpose = list(map(list, zip(*tens)))
    fig = sharex_rows(fig, tens_transpose)

    return fig

def add_column_titles(fig, tens, list_sites):
    """ Function adds column titles
    
    Parameters
    ----------
    fig : Figure
        figure with subplots
    tens : list
        list in the subplot shape that indicates the numbering of axes 
        for each subplot
    list_sites : list
        List of sites, 1 site per column
        will be used to label each column

    Returns
    -------
    fig : Figure
        figure with subplots
    """
    for ax, col in zip([fig.axes[m[0]] for m in tens[0]], list_sites):
        ax.set_title(col,fontdict={'fontsize': 20})
    # fig.tight_layout()

    return fig

def align_ylabels(fig, tens):
    """ Function aligns all left and right y labels
    
    Parameters
    ----------
    fig : Figure
        figure with subplots
    tens : list
        list in the subplot shape that indicates the numbering of axes 
        for each subplot

    Returns
    -------
    fig : Figure
        figure with subplots
    """
    fig.align_ylabels([fig.axes[m[0][0]] for m in tens])
    fig.align_ylabels([fig.axes[m[-1][-1]] for m in tens])
    # fig.tight_layout()

    return fig

def plot_same_new_figure(old_fig, new_ax_og):
    """ Function takes a Figure object and replots it identically

    Parameters
    ----------
    old_ax : matplotlib.axes._axes.Axes
        Axis of the original figure
    new_ax : matplotlib.axes._axes.Axes
        Axis of the new figure
    """
    for old_ax in old_fig.axes:
        new_ax = sharing_axis(new_ax_og, old_fig, old_ax)
        # recover_figsize(old_fig)

        # Re-plot Line2D objects
        recover_Line2D(old_ax, new_ax)

        # Recover x and y error bars
        recover_errorbars(old_ax, new_ax)

        # Recover hlines and vlines (horizontal and vertical liness)
        recover_hlines_vlines(old_ax, new_ax)

        # Re-plot fill_between (PolyCollection) objects
        recover_fill_between(old_ax, new_ax)

        # Recover all scatter plot data
        recover_scatter(old_ax, new_ax)

        # Recover all bar plot data
        recover_barplot(old_ax, new_ax)

        # Recover axis labels and title from the original axes
        # Recover tick labels (if any custom ticks were used)
        # Recover x and y limits from the original axes
        recover_axis_formatting(old_ax, new_ax)

        recover_axis_position(old_ax, new_ax)

        # Recover legend (if present)
        recover_legend(old_ax, new_ax)
