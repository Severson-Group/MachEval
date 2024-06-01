import os
import sys
import numpy as np
import matplotlib.pyplot as plt
from time import time as clock_time

os.chdir(os.path.dirname(__file__))
sys.path.append("../../../")

from mach_eval.analyzers.electromagnetic.flux_linkage_analyzer import Flux_Linkage_Problem, Flux_Linkage_Analyzer
from mach_eval.analyzers.electromagnetic.inductance_analyzer import Inductance_Problem, Inductance_Analyzer

from mach_cad.tools import jmag as JMAG

filepath = "C:/Users/filepath_of_FEA_file"
phasenames = ['U', 'V', 'W']
ratedcurrent = 20

####################################################
# 01 Setting project name and output folder
####################################################

toolJmag = JMAG.JmagDesigner()
toolJmag.visible = True
toolJmag.open(filepath + "/Example_FluxLinkage_Machine.jproj")

# Create output folder
results_filepath = filepath + "/run_data/"
if not os.path.isdir(results_filepath):
    os.makedirs(results_filepath)

project_name = "Machine_FluxLinkage_Project"
jmag_csv_folder = results_filepath

if not os.path.isdir(jmag_csv_folder):
    os.makedirs(jmag_csv_folder)

app = toolJmag.jd
model = app.GetCurrentModel()

# Pre-processing
model.SetName(project_name)

############################ Create Evaluator #####################
tic = clock_time()
flux_linkage_prob = Flux_Linkage_Problem(app, model, results_filepath, phasenames, ratedcurrent)
flux_linkage_analyzer = Flux_Linkage_Analyzer()
fea_data = flux_linkage_analyzer.analyze(flux_linkage_prob)
toc = clock_time()
print("Time spent on the flux linkage evaluation is %g min." % ((toc- tic)/60))

csv_folder = fea_data["csv_folder"]
study_name = fea_data["study_name"]
current_peak = fea_data["current_peak"]
rotor_angle = fea_data["rotor_angle"]
name_of_phases = fea_data["name_of_phases"]

print("\n************************ FLUX LINKAGE RESULTS ************************")
print("path = ", csv_folder)
print("study_name = ", study_name)
print("I_hat = ", current_peak, " A")
print("rotor_angle = ", rotor_angle[0], " deg")
print("name_of_phases = ", name_of_phases)
print("*************************************************************************\n")

tic = clock_time()
clarke_transformation_matrix = 2/3*np.array([[1, -1/2, -1/2], [0, np.sqrt(3)/2, -np.sqrt(3)/2], [1/2, 1/2, 1/2]])
inductance_prob = Inductance_Problem(current_peak, csv_folder, study_name, rotor_angle, name_of_phases)
inductance_analyzer = Inductance_Analyzer(clarke_transformation_matrix)
data = inductance_analyzer.analyze(inductance_prob)
toc = clock_time()
print("Time spent on the inductance evaluation is %g min." % ((toc- tic)/60))

rotor_angle = data["rotor_angle"]
Lalphabeta = data["Lalphabeta"]
Ldq = data["Ldq"]
L_d = np.mean(Ldq[:,0,0])
L_q = np.mean(Ldq[:,1,1])
saliency_ratio = L_d/L_q

fig1 = plt.figure()
ax1 = plt.axes()
fig1.add_axes(ax1)
ax1.plot(rotor_angle[0], Lalphabeta[:,0,0]*1000)
ax1.plot(rotor_angle[0], Lalphabeta[:,0,1]*1000)
ax1.plot(rotor_angle[0], Lalphabeta[:,1,0]*1000)
ax1.plot(rotor_angle[0], Lalphabeta[:,1,1]*1000)
ax1.plot(rotor_angle[0], Lalphabeta[:,2,2]*1000)
ax1.set_xlabel("Rotor Angle [deg]")
ax1.set_ylabel("Inductance [mH]")
ax1.set_title(r"$\alpha \beta \gamma$ Inductances")
plt.legend([r"$L_{\alpha \alpha}$", r"$L_{\alpha \beta}$", r"$L_{\beta \alpha}$", r"$L_{\beta \beta}$", r"$L_{\gamma \gamma}$"], fontsize=12)
plt.grid(True, linewidth=0.5, color="#A9A9A9", linestyle="-.")
plt.show()

fig2 = plt.figure()
ax2 = plt.axes()
fig2.add_axes(ax2)
plt.plot(rotor_angle[0], Ldq[:,0,0]*1000)
plt.plot(rotor_angle[0], Ldq[:,1,1]*1000)
plt.plot(rotor_angle[0], Ldq[:,2,2]*1000)
ax2.set_xlabel("Rotor Angle [deg]")
ax2.set_ylabel("Inductance [mH]")
ax2.set_title("dq0 Inductances")
plt.legend(["$L_d$", "$L_q$", "$L_0$"], fontsize=12)
plt.grid(True, linewidth=0.5, color="#A9A9A9", linestyle="-.")
plt.show()

print("\n************************ INDUCTANCE RESULTS ************************")
print("Ld = ", L_d*1000, " mH")
print("Lq = ", L_q*1000, " mH")
print("Saliency Ratio = ", saliency_ratio)
print("*************************************************************************\n")