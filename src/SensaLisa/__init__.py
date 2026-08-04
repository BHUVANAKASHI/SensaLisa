"""
SensaLisa
=========

A user-friendly Python toolkit for calculating and visualising
LISA sensitivity curves.
"""

from .sensitivity import (
    LISASensitivity,
    LISASensitivityFromWaveform,
)

__version__ = "0.1.0"

__all__ = [
    "LISASensitivity",
    "LISASensitivityFromWaveform",
]
