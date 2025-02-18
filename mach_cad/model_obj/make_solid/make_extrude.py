from .make_solid_base import MakeSolidBase
from ...tools.token_make import TokenMake
from ..dimensions.dim_linear import DimLinear

__all__ = ['MakeExtrude']



class MakeExtrude(MakeSolidBase):
    """Class defining how cross-sections are extruded"""
    def __init__(self, **kwargs: any) -> None:
        self._create_attr(kwargs)
        # validate attributes using parent class and this class's _validate_attr method
        super()._validate_attr()
        self._validate_attr()

    @property
    def dim_depth(self):
        return self._dim_depth

    def _validate_attr(self):
        if not isinstance(self._dim_depth, DimLinear):
            raise TypeError("Expected input to be one of the following type: \
                             DimLinear. Instead it was of type " + \
                            str(type(self._dim_depth)))


    def run(self, name, material, cs_token, maker):
        """Extrude cross-section to create component
        Args:
            name: Name given to component
            material: Material of component
            cs_token: List of CrossSectTokens from drawing component cross-section
            maker: Tool used to make 3D component
        """
        token1 = []
        for i in range(len(cs_token)):
            token1.append(maker.prepare_section(cs_token[i]))

        token2 = maker.extrude(name, material, self._dim_depth, self.location, token1)

        token_make = TokenMake(cs_token, token1, token2)
        return token_make
