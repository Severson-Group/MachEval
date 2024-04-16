import numpy as np

class SynRDesignSpace:
    def __init__(self, n_obj, bounds):
        self.__n_obj = n_obj
        self.__bounds = bounds

    @property
    def n_obj(self):
        return self.__n_obj

    @property
    def bounds(self):
        min_b, max_b = np.asarray(self.__bounds).T
        min_b, max_b = min_b.astype(float), max_b.astype(float)
        return min_b.tolist(), max_b.tolist()

    def get_objectives(self, full_results):
        valid_constraints = self.check_constraints(full_results)
        if not valid_constraints:
            f1, f2, f3 = 9999, 9999, 9999  # bad fitness values
        else:
            final_results = full_results[-1]
            final_state = final_results[-1]
            machine = final_state.design.machine
            em_results = final_state.conditions.em

            f1 = -1 * 0.001 * em_results['PRV'] # power per rotor volume [kW/m^3]
            f2 = -1 * em_results['efficiency'] #  efficiency [%]

            f3 = em_results['torque_ripple'] # torque ripple [%]
        return f1, f2, f3

    def check_constraints(self, full_results):
        valid_constraints = True
        final_results = full_results[-1]
        final_state = final_results[-1]
        em_results = final_state.conditions.em
        if abs(em_results['torque_ripple']) >= 0.5 or em_results['efficiency'] <= 0.93 or em_results['efficiency'] > 1:
            print('Constraints are violated:')
            print('\t torque_ripple: ', em_results['torque_ripple'], ', efficiency: ', em_results['efficiency'])
            valid_constraints = False
        return valid_constraints