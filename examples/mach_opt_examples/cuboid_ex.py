import os
import sys

# change current working directory to file location
os.chdir(os.path.dirname(__file__))
# add the directory immediately above this file's directory to path for module import
sys.path.append("../..")


from matplotlib import pyplot as plt
import mach_opt as mo
import pygmo as pg


class CuboidDesigner(mo.Designer):
    """Class converts input tuple x into a cuboid object"""

    def create_design(self, x: tuple) -> "Cuboid":
        """
        converts x tuple into a cuboid object.

        Args:
            x (tuple): Input free variables.
            
        Returns:
            cuboid (cuboid): cuboid object
        """

        L = x[0]
        W = x[1]
        H = x[2]
        cuboid = Cuboid(L, W, H)
        return cuboid


class Cuboid(mo.Design):
    """Class defines a cuboid object of Length and width
    
    Attributes:
        L (float): Length of cuboid.
        W (float): Width of cuboid.
        H (float); Height of cuboid
    """

    def __init__(self, L: float, W: float, H: float):
        """Creates cuboid object.

        Args:
            L (float): Length of cuboid
            W (float): Width of cuboid

        """
        self.L = L
        self.W = W
        self.H = H


class CuboidEval(mo.Evaluator):
    """"Class evaluates the cuboid object for volume and Surface Areas"""

    def evaluate(self, cuboid):
        """Evalute area and perimeter of cuboid

        Args:
            cuboid (cuboid): cuboid Object

        Returns:
            [V,SA,total,SA_Lateral] (List[float,float]): 
                Area and Perimeter of cuboidangle

        """
        V = cuboid.L * cuboid.W * cuboid.H
        SA_total = (
            2 * cuboid.L * cuboid.W + 2 * cuboid.W * cuboid.H + 2 * cuboid.L * cuboid.H
        )
        SA_Lateral = 2 * cuboid.W * cuboid.H + 2 * cuboid.L * cuboid.H
        return [V, SA_total, SA_Lateral]


class CuboidDesignSpace(mo.DesignSpace):
    """Class defines objectives of rectangle optimization"""

    def __init__(self, bounds, n_obj):
        self._n_obj = n_obj
        self._bounds = bounds

    def get_objectives(self, full_results) -> tuple:
        """ Calculates objectives from evaluation results
        

        Args:
            results (List(float,float)): Results from RectEval

        Returns:
            Tuple[float,float,float]: Maximize Volume,
                                      Minimize SA,
                                      Maximize Lateral SA
        """
        print(full_results)
        V=full_results[0]
        SA=full_results[1]
        SA_Lateral=full_results[2]
        return (-V, SA,-SA_Lateral)

    def check_constraints(self, full_results) -> bool:
        return True

    @property
    def n_obj(self) -> int:
        return self._n_obj

    @property
    def bounds(self) -> tuple:
        return self._bounds

class DataHandler:
    def save_to_archive(self, x, design, full_results, objs):
        """Unimplented data handler"""
        pass

    def save_designer(self, designer):
        pass

if __name__ == "__main__":
    des = CuboidDesigner()
    evaluator = CuboidEval()
    dh = DataHandler()
    bounds = ([0.5, 0.1, 0.25], [10, 3, 5])
    n_obj = 3
    ds= CuboidDesignSpace(bounds,n_obj)
    machDesProb = mo.DesignProblem(des, evaluator, ds, dh)
    opt = mo.DesignOptimizationMOEAD(machDesProb)
    pop_size = 465
    pop = opt.initial_pop(pop_size)
    gen_size = 10
    pop = opt.run_optimization(pop, gen_size)

    fits, vectors = pop.get_f(), pop.get_x()
    ndf, dl, dc, ndr = pg.fast_non_dominated_sorting(fits)

    fig1 = plt.figure()
    ax1 = fig1.add_subplot()
    im1 = ax1.scatter(fits[ndf[0], 0], fits[ndf[0], 1], c=fits[ndf[0], 2], marker="x")
    ax1.set_xlabel("-Volume")
    ax1.set_ylabel("Total Surface Area")
    ax1.set_title("Pareto Front")
    cb1 = fig1.colorbar(im1, ax=ax1,)
    cb1.set_label("-Lateral Surface Area")

    fig2 = plt.figure()
    ax2 = fig2.add_subplot()
    im2 = ax2.scatter(fits[ndf[0], 1], fits[ndf[0], 2], c=fits[ndf[0], 0], marker="x")
    ax2.set_xlabel("Total Surface Area")
    ax2.set_ylabel("-Lateral Surface Area")
    ax2.set_title("Pareto Front")
    cb2 = fig2.colorbar(im2, ax=ax2,)
    cb2.set_label("-Volume")

    fig3 = plt.figure()
    ax3 = fig3.add_subplot()
    im3 = ax3.scatter(fits[ndf[0], 2], fits[ndf[0], 0], c=fits[ndf[0], 1], marker="x")
    ax3.set_xlabel("-Lateral Surface Area")
    ax3.set_ylabel("-Volume")
    ax3.set_title("Pareto Front")
    cb3 = fig3.colorbar(im3, ax=ax3,)
    cb3.set_label("Total Surface Area")

