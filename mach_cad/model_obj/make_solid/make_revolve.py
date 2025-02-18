from .make_solid_base import MakeSolidBase
from ...tools.token_make import TokenMake
from ..dimensions.dim_angular import DimAngular
from ..location_2d import Location2D

__all__ = ["MakeRevolve"]


class MakeRevolve(MakeSolidBase):
    """Class defining how cross-sections are revolved"""

    def __init__(self, **kwargs: any) -> None:
        self._create_attr(kwargs)
        # validate attributes using parent class and this class's _validate_attr method
        super()._validate_attr()
        self._validate_attr()

    @property
    def dim_angle(self):
        return self._dim_angle

    @property
    def dim_center(self):
        return self._dim_center

    @property
    def dim_axis(self):
        return self._dim_axis

    def _validate_attr(self):
        if not isinstance(self._dim_angle, DimAngular):
            raise TypeError(
                "Expected input to be one of the following type: \
                             DimAngular. Instead it was of type "
                + str(type(self._dim_angle))
            )

        if not isinstance(self._dim_center, Location2D):
            raise TypeError(
                "Expected input to be one of the following type: \
                             Location2D. Instead it was of type "
                + str(type(self._dim_center))
            )

        if not isinstance(self._dim_axis, Location2D):
            raise TypeError(
                "Expected input to be one of the following type: \
                             Location2D. Instead it was of type "
                + str(type(self._dim_axis))
            )

    def run(self, name, material, cs_token, maker):
        """Revolve cross-section to create 3D component

        Args:
            name: Name given to component
            material: Material of component
            cs_token: List of CrossSectTokens from drawing component cross-section
            maker: Tool used to make 3D component
        """
        token1 = []
        for i in range(len(cs_token)):
            token1.append(maker.prepare_section(cs_token[i]))

        token2 = maker.revolve(
            name, material, self._dim_center, self._dim_axis, self._dim_angle, token1
        )

        token_make = TokenMake(cs_token, token1, token2)

        token_make = TokenMake(cs_token, token1, token2)
        return token_make
