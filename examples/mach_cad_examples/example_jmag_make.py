import os
import sys

# change current working directory to file location
os.chdir(os.path.dirname(__file__))
# add the directory immediately above this file's directory to path for module import
sys.path.append("../..")

import mach_cad.tools.jmag as jd
import mach_cad.model_obj as mo

stator1 = mo.CrossSectOuterRotorStator(
    name="stator1",
    dim_alpha_st=mo.DimDegree(30),
    dim_alpha_so=mo.DimDegree((30 / 2) * 0.25),
    dim_r_si=mo.DimMillimeter(15),
    dim_d_sy=mo.DimMillimeter(7.5),
    dim_d_st=mo.DimMillimeter(7.5),
    dim_d_sp=mo.DimMillimeter(5),
    dim_d_so=mo.DimMillimeter(3),
    dim_w_st=mo.DimMillimeter(7.5),
    dim_r_st=mo.DimMillimeter(0),
    dim_r_sf=mo.DimMillimeter(0),
    dim_r_sb=mo.DimMillimeter(0),
    dim_Q=8,
    location=mo.Location2D(anchor_xy=[mo.DimMillimeter(0), mo.DimMillimeter(0)]),
    theta=mo.DimDegree(0),
)

stator2 = mo.CrossSectOuterRotorStator(
    name="stator2",
    dim_alpha_st=mo.DimDegree(30),
    dim_alpha_so=mo.DimDegree((30 / 2) * 0.25),
    dim_r_si=mo.DimMillimeter(15),
    dim_d_sy=mo.DimMillimeter(7.5),
    dim_d_st=mo.DimMillimeter(7.5),
    dim_d_sp=mo.DimMillimeter(5),
    dim_d_so=mo.DimMillimeter(3),
    dim_w_st=mo.DimMillimeter(7.5),
    dim_r_st=mo.DimMillimeter(0),
    dim_r_sf=mo.DimMillimeter(0),
    dim_r_sb=mo.DimMillimeter(0),
    dim_Q=8,
    location=mo.Location2D(anchor_xy=[mo.DimMillimeter(100), mo.DimMillimeter(0)]),
    theta=mo.DimDegree(0),
)

comp1 = mo.Component(
    name="comp1",
    cross_sections=[stator1],
    material=mo.MaterialGeneric(name="10JNEX900"),
    make_solid=mo.MakeExtrude(location=mo.Location3D(anchor_xyz=[mo.DimMillimeter(0), mo.DimMillimeter(0), mo.DimMillimeter(10)]), dim_depth=mo.DimMillimeter(15)),
)

comp2 = mo.Component(
    name="comp2",
    cross_sections=[stator2],
    material=mo.MaterialGeneric(name="10JNEX900"),
    make_solid=mo.MakeExtrude(location=mo.Location3D(anchor_xyz=[mo.DimMillimeter(0), mo.DimMillimeter(0), mo.DimMillimeter(-10)]), dim_depth=mo.DimMillimeter(15)),
)

file = r"trial100.jproj"

tool_jmag = jd.JmagDesigner()
tool_jmag.open(comp_filepath=file)
tool_jmag.set_visibility(True)
comp1.make(tool_jmag, tool_jmag)
comp2.make(tool_jmag, tool_jmag)
tool_jmag.save()
