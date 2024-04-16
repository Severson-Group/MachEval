import os

from my_data_handler import MyDataHandler
from my_plotting_functions import DataAnalyzer

# for box plot
import matplotlib.pyplot as plt

path = os.path.dirname(__file__)
arch_file = path + r'/opti_arch.pkl'  # specify path where saved data will reside
des_file = path + r'/opti_designer.pkl'
dh = MyDataHandler(arch_file, des_file)  # initialize data handler with required file paths

fitness, free_vars = dh.get_pareto_fitness_freevars()

da = DataAnalyzer(path)

# Plot pareto front - 3 variations

# get rid of designs that violate constraints
for i in range(len(fitness)):
    if fitness[i][1] > -0.75 or fitness[i][1] < -1 or fitness[i][2] > 0.5:
        fitness[i] = [None,None,None]

da.plot_pareto_front(points=fitness, label=['-PRV [kW/m^3]', '-$\eta$ [%]', 'Trip []'], saveName='/paretoPlot1.svg')

i = 0
fitness2 = [[0 for x in range(3)] for y in range(len(fitness))] 
for data in fitness:
    fitness2[i][0] = fitness[i][1]
    fitness2[i][1] = fitness[i][2]
    fitness2[i][2] = fitness[i][0]
    i = i + 1
da.plot_pareto_front(points=fitness2, label=['-$\eta$ [%]', 'Trip []', '-PRV [kW/m^3]'], saveName='/paretoPlot2.svg')

i = 0
fitness3 = [[0 for x in range(3)] for y in range(len(fitness))]
for data in fitness:
    fitness3[i][0] = fitness[i][2]
    fitness3[i][1] = fitness[i][0]
    fitness3[i][2] = fitness[i][1]
    i = i + 1
da.plot_pareto_front(points=fitness3, label=['Trip []', '-PRV [kW/m^3]', '-$\eta$ [%]'], saveName='/paretoPlot3.svg')

# plot free vars plot
fitness, free_vars = dh.get_archive_data()
var_label = [
            '$r_{ri}$ [m]',
            "$r_{ro}$ [m]",
            '$d_{r1}$ [m]',
            '$d_{r2}$ [m]',
            '$w_{b1}$ [m]',
            '$w_{b2}$ [m]',
            '$l_{b1}$ [m]',
            '$l_{b2}$ [m]',
            '$l_{b4}$ [m]',
            '$l_{b5}$ [m]',
            ]

dims = (6e-3, 50e-3, 8e-3, 8e-3, 4e-3, 4e-3, 34e-3, 20e-3, 15e-3, 10e-3)
# bounds for pygmo optimization problem
bounds = [
    [0.5 * dims[0], 2 * dims[0]],  # r_ri
    [0.9 * dims[1], 1 * dims[1]],  # r_ro
    [0.5 * dims[2], 2 * dims[2]],  # d_r1
    [0.5 * dims[3], 2 * dims[3]],  # d_r2
    [0.5 * dims[4], 1.5 * dims[4]],  # w_b1
    [0.5 * dims[5], 1.5 * dims[5]],  # w_b2
    [0.5 * dims[2], 1.5 * dims[2]],  # l_b1
    [0.5 * dims[3], 1.5 * dims[3]],  # l_b2
    [0.75 * dims[4], 1.5 * dims[4]],  # l_b4
    [0.75 * dims[5], 1.5 * dims[5]],  # l_b5
]

# Create box plots for free vars 

var_label = [
            r'$r_{ri}$ [mm]',
            r"$r_{ro}$ [mm]",
            r'$d_{r1}$ [mm]',
            r'$d_{r2}$ [mm]',
            r'$w_{b1}$ [mm]',
            r'$w_{b2}$ [mm]',
            r'$l_{b1}$ [mm]',
            r'$l_{b2}$ [mm]',
            r'$l_{b4}$ [mm]',
            r'$l_{b5}$ [mm]',
            ]

fig = plt.figure(figsize =(10, 7))
xt = [[0 for x in range(len(free_vars[0]))] for y in range(len(free_vars))]

for j in range(len(free_vars[0])):
    xt[j] = [x[j] for x in free_vars]
     
    # Creating plot
    plt.boxplot(xt[j])

# generate data

# create a list of data to plot
data_to_plot = [xt[0], xt[1], xt[2], xt[3], xt[4], xt[5], xt[6], xt[7], xt[8], xt[9]]
fig, axes = plt.subplots(nrows=1, ncols=10, sharey=False, figsize=(13, 3))
c = 'tan'
for i, ax in enumerate(axes):
    ax.boxplot([data_to_plot[i]], showfliers=False, patch_artist=True,
            boxprops=dict(facecolor=c, color='red'),
            capprops=dict(color=c),
            whiskerprops=dict(color='red'),
            medianprops=dict(color='red'),)
    ax.set_xticks([])
    ax.set_xlabel(var_label[i])
    ax.ticklabel_format(axis="y", scilimits=(0,0), useMathText=True, style='sci')

fig.tight_layout()
plt.savefig(path + '/boxPlotFreeVar.svg')    

# Parameter sensitivity analysis
label=['-PRV [kW/m^3]', '-$\eta$ [%]', 'Trip []']

# get rid of designs that violate constraints
for i in range(len(fitness)):
    if fitness[i][1] > -0.50 or fitness[i][1] < -1 or fitness[i][2] > 0.5:
        fitness[i] = [None,None,None]
            
fit = [[0 for x in range(len(fitness[0]))] for y in range(len(fitness))]
for j in range(len(fitness[0])):
    fit[j] = [x[j] for x in fitness]

da.plot_XY_sensitivity(xt, fit[0], marker='o', ax=None, fig=None, var_label=var_label, obj_label='-PRV [kW/m^3]', saveas='/xySensPRV.svg', s=5)
da.plot_XY_sensitivity(xt, fit[1], marker='o', ax=None, fig=None, var_label=var_label, obj_label='-$\eta$ [%]', saveas='/xySensEff.svg', s=5)
da.plot_XY_sensitivity(xt, fit[2], marker='o', ax=None, fig=None, var_label=var_label, obj_label='T_rip', saveas='/xySensTrip.svg', s=5)