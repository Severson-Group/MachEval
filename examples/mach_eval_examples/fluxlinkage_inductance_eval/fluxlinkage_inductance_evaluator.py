import os
import sys
import numpy as np
import matplotlib.pyplot as plt
from time import time as clock_time

os.chdir(os.path.dirname(__file__))
sys.path.append("../../../")

from mach_eval.analyzers.electromagnetic.flux_linkage_analyzer import FluxLinkageJMAG_Problem, FluxLinkageJMAG_Analyzer
from mach_eval.analyzers.electromagnetic.inductance_analyzer import InductanceProblem, InductanceAnalyzer

from mach_cad.tools import jmag as JMAG

filepath = "C:/Users/dante/Documents/github_repos/eMach/examples/mach_eval_examples/fluxlinkage_inductance_eval"
phasenames = ['U', 'V', 'W']
rated_current = 20

####################################################
# 01 Setting project name and output folder
####################################################

toolJmag = JMAG.JmagDesigner()
toolJmag.visible = True
toolJmag.open(filepath + "/Example_FluxLinkage_Machine.jproj")

############################ Create Evaluator #####################
tic = clock_time()
flux_linkage_prob = FluxLinkageJMAG_Problem(toolJmag, phasenames, rated_current)
flux_linkage_analyzer = FluxLinkageJMAG_Analyzer()
fea_data = flux_linkage_analyzer.analyze(flux_linkage_prob)
toc = clock_time()
print("Time spent on the flux linkage evaluation is %g min." % ((toc- tic)/60))

linkages = fea_data["linkages"]
current_peak = fea_data["current_peak"]
rotor_angle = fea_data["rotor_angle"]
name_of_phases = fea_data["name_of_phases"]

print("\n************************ FLUX LINKAGE RESULTS ************************")
print("Linkages = ", linkages)
print("I_hat = ", current_peak, " A")
print("rotor_angle = ", rotor_angle[0], " deg")
print("name_of_phases = ", name_of_phases)
print("*************************************************************************\n")

clarke_transformation_matrix = 2/3*np.array([[1, -1/2, -1/2], [0, np.sqrt(3)/2, -np.sqrt(3)/2], [1/2, 1/2, 1/2]])
inductance_prob = InductanceProblem(current_peak, linkages, rotor_angle, name_of_phases)
inductance_analyzer = InductanceAnalyzer(clarke_transformation_matrix)
data = inductance_analyzer.analyze(inductance_prob)

rotor_angle = data["rotor_angle"]
Labc = data["Labc"]
Lalphabeta = data["Lalphabeta"]
Ldq = data["Ldq"]
L_d = np.mean(Ldq[:,0,0])
L_q = np.mean(Ldq[:,1,1])
saliency_ratio = L_d/L_q

fig1 = plt.figure()
ax1 = plt.axes()
fig1.add_axes(ax1)
ax1.plot(rotor_angle[0], Labc[0,0,:]*1000)
ax1.plot(rotor_angle[0], Labc[1,1,:]*1000)
ax1.plot(rotor_angle[0], Labc[2,2,:]*1000)
ax1.set_xlabel("Rotor Angle [deg]")
ax1.set_ylabel("Inductance [mH]")
ax1.set_title("abc Inductances")
plt.legend(["$L_a$", "$L_b$", "$L_c$"], fontsize=12, loc='center right')
plt.grid(True, linewidth=0.5, color="#A9A9A9", linestyle="-.")
plt.show()

fig2 = plt.figure()
ax2 = plt.axes()
fig2.add_axes(ax2)
ax2.plot(rotor_angle[0], Lalphabeta[:,0,0]*1000)
ax2.plot(rotor_angle[0], Lalphabeta[:,1,1]*1000)
ax2.plot(rotor_angle[0], Lalphabeta[:,2,2]*1000)
ax2.set_xlabel("Rotor Angle [deg]")
ax2.set_ylabel("Inductance [mH]")
ax2.set_title(r"$\alpha \beta \gamma$ Inductances")
plt.legend([r"$L_{\alpha \alpha}$", r"$L_{\beta \beta}$", r"$L_{\gamma \gamma}$"], fontsize=12, loc='center right')
plt.grid(True, linewidth=0.5, color="#A9A9A9", linestyle="-.")
plt.show()

fig3 = plt.figure()
ax3 = plt.axes()
fig3.add_axes(ax3)
ax3.plot(rotor_angle[0], Ldq[:,0,0]*1000)
ax3.plot(rotor_angle[0], Ldq[:,1,1]*1000)
ax3.plot(rotor_angle[0], Ldq[:,2,2]*1000)
ax3.set_xlabel("Rotor Angle [deg]")
ax3.set_ylabel("Inductance [mH]")
ax3.set_title("dq0 Inductances")
plt.legend(["$L_d$", "$L_q$", "$L_0$"], fontsize=12, loc='center right')
plt.grid(True, linewidth=0.5, color="#A9A9A9", linestyle="-.")
plt.show()

print("\n************************ INDUCTANCE RESULTS ************************")
print("Ld = ", L_d*1000, " mH")
print("Lq = ", L_q*1000, " mH")
print("Saliency Ratio = ", saliency_ratio)
print("*************************************************************************\n")