"""Module holding the abstract base classes defining the contracts eMach tools are expected to uphold."""

from abc import ABC, abstractmethod
from typing import Tuple


class ToolBase(ABC):
    """Abstract base class defining basic methods required of an eMach tool."""

    @abstractmethod
    def open(self, filename: str, length_unit: str, angle_unit: str) -> any:
        """Required method in eMach tools to open tool application instances."""
        pass

    @abstractmethod
    def save(self):
        """Saves current instance of tool application which was already a file on disk."""
        pass

    @abstractmethod
    def save_as(self, filename: str):
        """Saves current instance of tool application as a new file."""
        pass

    @abstractmethod
    def close(self):
        """Closes current instance of tool application without saving."""
        pass


class DrawerBase(ABC):
    """Abstract base class defining methods required by eMach tools to draw 2D cross-sections."""
    @abstractmethod
    def draw_line(self, startxy: 'Location2D', endxy: 'Location2D') -> 'TokenDraw':
        """Function to draw a line.

        Args:
            startxy: Start point of line. Should be of type Location2D defined with eMach dimensions.
            endxy: End point of the. Should be of type Location2D defined with eMach dimensions.
        Returns:
            TokenDraw: Wrapper object holding return values obtained from tool upon drawing a line.
        """
        pass

    @abstractmethod
    def draw_arc(self, centerxy: 'Location2D', startxy: 'Location2D', endxy: 'Location2D') -> 'TokenDraw':
        """Function to draw an arc.

            Args:
                centerxy: Centre point of arc. Should be of type Location2D defined with eMach dimensions.
                startxy: Start point of arc. Should be of type Location2D defined with eMach dimensions.
                endxy: End point of arc. Should be of type Location2D defined with eMach dimensions.
            Returns:
                TokenDraw: Wrapper object holding return values obtained from tool upon drawing an arc.
            """
        pass

    @abstractmethod
    def select(self): pass


class MakerBase(ABC):
    """Abstract base class defining method(s) required by eMach tools to draw 3D components"""
    @abstractmethod
    def prepare_section(self, cs_token: 'CrossSectToken') -> any:
        """Function to select a cross-section"""
        pass


class MakerExtrudeBase(MakerBase):
    """Abstract base class defining method(s) to extrude cross-sections in eMach tools"""
    @abstractmethod
    def extrude(self, name: str, material: str, depth: 'DimLinear') -> any:
        pass


class MakerRevolveBase(MakerBase):
    """Abstract base class defining method(s) to revolve cross-sections in eMach tools"""
    @abstractmethod
    def revolve(self, name: str, material: str, center: 'Location2D', axis: 'Location2D', angle: float) -> any: pass
