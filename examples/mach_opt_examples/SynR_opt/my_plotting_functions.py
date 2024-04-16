import matplotlib.pyplot as plt
import matplotlib.ticker as mtick
import pygmo as pg
import numpy as np

class DataAnalyzer:
    def __init__(self, save_path):
        self.save_path = save_path

    def plot_pareto_front(self, points, marker='o', xy=[0, 1], no_text=True, up_to_rank_no=1, ax=None, fig=None, no_colorbar=False, z_filter=None, label=None, saveName='/paretoPlot.svg'):
        plt.rcParams['mathtext.fontset'] = 'stix' # 'cm'
        plt.rcParams["font.family"] = "Times New Roman"

        font = {'family' : 'Times New Roman', #'serif',
                'color' : 'black',
                'weight' : 'normal',
                'size' : 14,}

        from mpl_toolkits.axes_grid1 import make_axes_locatable
        from mpl_toolkits.axes_grid1.inset_locator import inset_axes

        full_comp = [0, 1, 2]
        full_comp.remove(xy[0])
        full_comp.remove(xy[1])
        z_comp = full_comp[0]
        print(points)
        fronts, _, _, _= pg.fast_non_dominated_sorting(points)

        # We define the colors of the fronts (grayscale from black to white)
        cl = list(zip(np.linspace(0.9, 0.1, len(fronts)),
                      np.linspace(0.9, 0.1, len(fronts)),
                      np.linspace(0.9, 0.1, len(fronts))))

        if ax is None:
            fig, ax = plt.subplots(figsize=(3.8, 4),constrained_layout=False)
            plt.subplots_adjust(left=None, bottom=None, right=0.85, top=None, wspace=None, hspace=None)

        count = 0
        for ndr, front in enumerate(fronts):
            count += 1

            # Frist compute the points coordinates
            x_scale = 1
            y_scale = 1
            z_scale = 1
            x = [points[idx][xy[0]] for idx in front]
            y = [points[idx][xy[1]] for idx in front]
            z = [points[idx][z_comp]  for idx in front]

            # Then sort them by the first objective
            tmp = [(a, b, c) for a, b, c in zip(x, y, z)]
            tmp = sorted(tmp, key=lambda k: k[0])

            # Now plot using step
            ax.step([coords[0] for coords in tmp], 
                    [coords[1] for coords in tmp], color=cl[ndr], where='post')

            # Now add color according to the value of the z-axis variable usign scatter
            if z_filter is not None:
                z = np.array(z)
                x = np.array(x)[z<z_filter]
                y = np.array(y)[z<z_filter]
                z = z[z<z_filter]
                print('-Power Density, -Efficency, Torque Ripple')
                for a,b,c in zip(x,y,z):
                    print(a,b,c)
                scatter_handle = ax.scatter(x, y, c=z, s=40,  edgecolor=None, alpha=0.5, cmap='viridis', marker=marker, zorder=99, vmin=0, vmax=20, label=label,markersize=20) #'viridis'    Spectral
            else:
                scatter_handle = ax.scatter(x, y, c=z, s=40, edgecolor=None, alpha=0.5, cmap='viridis', marker=marker, zorder=99) #'viridis'

            if up_to_rank_no is None:
                pass
            else:
                if count >= up_to_rank_no:
                    break

        ax.xaxis.set_major_locator(mtick.MaxNLocator(6))
        axins = inset_axes(ax,
                            width="3%",  # width = 5% of parent_bbox width
                            height="100%",  # height : 50%
                            loc='lower left',
                            bbox_to_anchor=(1, 0., 1, 1),
                            bbox_transform=ax.transAxes,
                            borderpad=0,
                            )

        clb = fig.colorbar(scatter_handle, cax=axins)
        z_text  = '%.1f'

        if not no_colorbar:
            clb.ax.set_ylabel(label[z_comp], rotation=0, labelpad=20, **font)
            clb.ax.yaxis.set_label_coords(-1,1.085)
            clb.ax.yaxis.set_major_locator(mtick.MaxNLocator(6))


        # refine the plotting
        ax.set_xlabel(label[xy[0]], **font)        
        ax.set_ylabel(label[xy[1]], **font,rotation=0)

        ax.yaxis.set_label_coords(-0.1,1.055)
        plt.yticks(rotation=90)
        ax.yaxis.set_major_locator(mtick.MaxNLocator(6))

        ax.grid()
        ax.tick_params(axis='both', which='major', labelsize=14)
        clb.ax.tick_params(which='major', labelsize=14, rotation=0)
        plt.gcf().subplots_adjust(bottom=0.15)
        fig.savefig(self.save_path + saveName, bbox_inches='tight', dpi=300)


    def plot_XY_sensitivity(self, free_vars, Obj, marker='o', ax=None, fig=None, var_label=None, obj_label=None, saveas=None, s=5):
        plt.rcParams['mathtext.fontset'] = 'stix' # 'cm'
        plt.rcParams["font.family"] = "Times New Roman"

        font = {'family' : 'Times New Roman', #'serif',
                'color' : 'black',
                'weight' : 'normal',
                'size' : 14,}

        from mpl_toolkits.axes_grid1 import make_axes_locatable
        from mpl_toolkits.axes_grid1.inset_locator import inset_axes


        if ax is None:
            fig, ax = plt.subplots(nrows=1, ncols=10, sharey=True, figsize=(13, 3),constrained_layout=False)
            plt.subplots_adjust(left=None, bottom=None, right=0.85, top=None, wspace=None, hspace=None)

        for i, axes in enumerate(ax):
            axes.scatter(free_vars[i], Obj, s=s, edgecolor="face", alpha=0.5, cmap='viridis', marker=marker, zorder=99)
            plt.gcf().subplots_adjust(bottom=0.2)
            axes.set_xlabel(var_label[i], **font)
            axes.xaxis.set_major_locator(mtick.MaxNLocator(2))
            axes.yaxis.set_major_locator(mtick.MaxNLocator(6))

            axes.grid()
            axes.tick_params(axis='both', which='major', labelsize=14)

        fig.text(-0.01, 0.6, obj_label, va='center', rotation='vertical', **font)
        fig.tight_layout()
        plt.gcf().subplots_adjust(bottom=0.25)
        fig.savefig(self.save_path + saveas, bbox_inches='tight', dpi=300)