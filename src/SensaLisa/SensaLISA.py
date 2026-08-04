"""
SensaLisa: Utilities for calculating LISA sensitivity curves.

This module provides two user-facing classes:

1. LISASensitivityFromWaveform
   Evaluates the LISA noise model at frequencies supplied by a waveform model.
   This is useful for waveform comparisons and signal-to-noise ratio
   calculations.

2. LISASensitivity
   Generates a standard logarithmically spaced frequency array and evaluates
   the LISA sensitivity across the detector's frequency band.
"""

from __future__ import annotations

from typing import Iterable

import matplotlib.pyplot as plt
import numpy as np
from numpy.typing import ArrayLike, NDArray


class _LISANoiseModel:
    """
    Internal base class containing the common LISA noise calculations.

    This class is not intended to be instantiated directly. The public
    interfaces are `LISASensitivityFromWaveform` and `LISASensitivity`.
    """

    ARM_LENGTH = 2.5e9  # LISA arm length in meters
    TRANSFER_FREQUENCY = 19.09e-3  # Approximate transfer frequency in Hz
    CONFUSION_AMPLITUDE = 9.0e-45

    CONFUSION_PARAMETERS = {
        "6mo": {
            "alpha": 0.133,
            "beta": 243.0,
            "kappa": 482.0,
            "gamma": 917.0,
            "f_knee": 0.00258,
        },
        "1yr": {
            "alpha": 0.171,
            "beta": 292.0,
            "kappa": 1020.0,
            "gamma": 1680.0,
            "f_knee": 0.00215,
        },
        "2yr": {
            "alpha": 0.165,
            "beta": 299.0,
            "kappa": 611.0,
            "gamma": 1340.0,
            "f_knee": 0.00173,
        },
        "4yr": {
            "alpha": 0.138,
            "beta": -221.0,
            "kappa": 521.0,
            "gamma": 1680.0,
            "f_knee": 0.00113,
        },
    }

    def __init__(
        self,
        frequencies: ArrayLike,
        observation_time: str = "1yr",
    ) -> None:
        """
        Initialize the LISA noise model.

        Parameters
        ----------
        frequencies
            Frequencies in Hz at which the LISA noise should be evaluated.
        observation_time
            Observation duration used for the Galactic confusion-noise model.
            Supported values are "6mo", "1yr", "2yr", and "4yr".
        """
        self.observation_time = self._validate_observation_time(
            observation_time
        )
        self.frequencies = self._validate_frequencies(frequencies)

        # Calculate and store the individual noise contributions.
        self.instrumental_psd = self._compute_instrumental_psd()
        self.confusion_psd = self._compute_confusion_psd()

        # Total one-sided noise power spectral density.
        self.psd = self.instrumental_psd + self.confusion_psd

        # Amplitude spectral density: sqrt(S_n).
        self.asd = np.sqrt(self.psd)

        # Characteristic noise strain: sqrt(f S_n).
        self.characteristic_strain = np.sqrt(self.frequencies * self.psd)

        # Backward-compatible name. In the original implementation,
        # "sensitivity" represented the amplitude spectral density.
        self.sensitivity = self.asd

    @classmethod
    def _validate_observation_time(cls, observation_time: str) -> str:
        """Validate the requested observation duration."""
        if observation_time not in cls.CONFUSION_PARAMETERS:
            valid_options = ", ".join(cls.CONFUSION_PARAMETERS)
            raise ValueError(
                f"Invalid observation time '{observation_time}'. "
                f"Choose from: {valid_options}."
            )

        return observation_time

    @staticmethod
    def _validate_frequencies(
        frequencies: ArrayLike,
    ) -> NDArray[np.float64]:
        """Convert the input to a finite, positive NumPy array."""
        frequency_array = np.asarray(frequencies, dtype=float)

        if frequency_array.ndim != 1:
            raise ValueError("Frequencies must be a one-dimensional array.")

        if frequency_array.size == 0:
            raise ValueError("The frequency array cannot be empty.")

        if not np.all(np.isfinite(frequency_array)):
            raise ValueError(
                "Frequencies must not contain NaN or infinite values."
            )

        if np.any(frequency_array <= 0.0):
            raise ValueError("All frequencies must be greater than zero.")

        return frequency_array

    def _compute_instrumental_psd(self) -> NDArray[np.float64]:
        """
        Calculate the instrumental LISA noise power spectral density.

        Returns
        -------
        numpy.ndarray
            Instrumental noise PSD in 1/Hz.
        """
        f = self.frequencies
        length = self.ARM_LENGTH
        f_star = self.TRANSFER_FREQUENCY

        # Optical metrology system displacement noise.
        p_oms = (1.5e-11) ** 2 * (
            1.0 + (2.0e-3 / f) ** 4
        )

        # Test-mass acceleration noise.
        p_acc = (3.0e-15) ** 2 * (
            1.0 + (0.4e-3 / f) ** 2
        ) * (
            1.0 + (f / 8.0e-3) ** 4
        )

        # Equivalent fractional-frequency noise.
        p_n = (
            p_oms
            + (
                2.0
                * (1.0 + np.cos(f / f_star) ** 2)
                * p_acc
                / (2.0 * np.pi * f) ** 4
            )
        ) / length**2

        # Approximate sky-averaged detector response.
        response = (
            3.0
            / 10.0
            / (1.0 + 0.6 * (f / f_star) ** 2)
        )

        return p_n / response

    def _compute_confusion_psd(self) -> NDArray[np.float64]:
        """
        Calculate the Galactic confusion-noise power spectral density.

        Returns
        -------
        numpy.ndarray
            Galactic confusion-noise PSD in 1/Hz.
        """
        f = self.frequencies
        parameters = self.CONFUSION_PARAMETERS[
            self.observation_time
        ]

        alpha = parameters["alpha"]
        beta = parameters["beta"]
        kappa = parameters["kappa"]
        gamma = parameters["gamma"]
        f_knee = parameters["f_knee"]

        exponent = (
            -alpha * f
            + beta * f * np.sin(kappa * f)
        )

        # Clipping protects the exponential from numerical overflow.
        exponent = np.clip(exponent, -100.0, 100.0)

        with np.errstate(over="ignore", invalid="ignore"):
            confusion_psd = (
                self.CONFUSION_AMPLITUDE
                * f ** (-7.0 / 3.0)
                * np.exp(exponent)
                * (
                    1.0
                    + np.tanh(gamma * (f_knee - f))
                )
            )

        return np.nan_to_num(
            confusion_psd,
            nan=0.0,
            posinf=0.0,
            neginf=0.0,
        )

    def get_psd(
        self,
    ) -> tuple[NDArray[np.float64], NDArray[np.float64]]:
        """
        Return frequencies and the total noise PSD.

        The PSD is normally the quantity required in matched-filter
        signal-to-noise ratio calculations.
        """
        return self.frequencies.copy(), self.psd.copy()

    def get_asd(
        self,
    ) -> tuple[NDArray[np.float64], NDArray[np.float64]]:
        """Return frequencies and amplitude spectral density."""
        return self.frequencies.copy(), self.asd.copy()

    def get_characteristic_strain(
        self,
    ) -> tuple[NDArray[np.float64], NDArray[np.float64]]:
        """Return frequencies and characteristic noise strain."""
        return (
            self.frequencies.copy(),
            self.characteristic_strain.copy(),
        )

    def get_data(
        self,
    ) -> tuple[NDArray[np.float64], NDArray[np.float64]]:
        """
        Return frequencies and amplitude spectral density.

        This method preserves the behavior of the original implementation.
        For new code, prefer `get_psd()`, `get_asd()`, or
        `get_characteristic_strain()`.
        """
        return self.get_asd()

    def plot(
        self,
        quantity: str = "asd",
        show_components: bool = False,
        save_fig: bool = False,
        filename: str = "lisa_sensitivity.png",
    ) -> None:
        """
        Plot the selected LISA noise quantity.
    
        Parameters
        ----------
        quantity
            Quantity to plot. Supported values are:
            - "psd": power spectral density
            - "asd": amplitude spectral density
            - "characteristic_strain": characteristic noise strain
        show_components
            When plotting the PSD or ASD, also display the instrumental
            and Galactic confusion-noise components.
        save_fig
            If True, save the figure to disk.
        filename
            Name or path of the saved figure. The file format is determined
            from the extension, for example ".png", ".pdf", or ".svg".
        """
        valid_quantities = {
            "psd",
            "asd",
            "characteristic_strain",
        }
    
        if quantity not in valid_quantities:
            raise ValueError(
                f"Invalid quantity '{quantity}'. "
                f"Choose from: {', '.join(sorted(valid_quantities))}."
            )
    
        figure, axis = plt.subplots(figsize=(10, 6))
    
        if quantity == "psd":
            values = self.psd
            ylabel = r"Noise PSD $S_n(f)$ [$1/\mathrm{Hz}$]"
    
            axis.loglog(
                self.frequencies,
                values,
                label="Total LISA noise",
            )
    
            if show_components:
                axis.loglog(
                    self.frequencies,
                    self.instrumental_psd,
                    linestyle="--",
                    label="Instrumental noise",
                )
                axis.loglog(
                    self.frequencies,
                    self.confusion_psd,
                    linestyle=":",
                    label="Galactic confusion noise",
                )
    
        elif quantity == "asd":
            values = self.asd
            ylabel = (
                r"Amplitude spectral density "
                r"$\sqrt{S_n(f)}$ [$1/\sqrt{\mathrm{Hz}}$]"
            )
    
            axis.loglog(
                self.frequencies,
                values,
                label="LISA sensitivity",
            )
    
            if show_components:
                axis.loglog(
                    self.frequencies,
                    np.sqrt(self.instrumental_psd),
                    linestyle="--",
                    label="Instrumental noise",
                )
                axis.loglog(
                    self.frequencies,
                    np.sqrt(self.confusion_psd),
                    linestyle=":",
                    label="Galactic confusion noise",
                )
    
        else:
            values = self.characteristic_strain
            ylabel = r"Characteristic noise strain $\sqrt{fS_n(f)}$"
    
            axis.loglog(
                self.frequencies,
                values,
                label="LISA characteristic noise strain",
            )
    
        axis.set_xlabel("Frequency [Hz]")
        axis.set_ylabel(ylabel)
        axis.set_title(
            f"LISA Sensitivity Curve ({self.observation_time})"
        )
        axis.grid(
            True,
            which="both",
            linestyle="--",
            linewidth=0.5,
        )
        axis.legend()
    
        figure.tight_layout()
    
        if save_fig:
            figure.savefig(
                filename,
                dpi=300,
                bbox_inches="tight",
            )
            print(f"Figure saved as: {filename}")
    
        plt.show()

# ---------------------------------------------------------------------------
# Waveform-frequency interface
# ---------------------------------------------------------------------------
class LISASensitivityFromWaveform(_LISANoiseModel):
    """
    Evaluate LISA sensitivity at frequencies supplied by a waveform model.

    This class is intended for gravitational-wave analyses in which the
    frequency array has already been generated by a waveform model. It
    evaluates the LISA noise at exactly those frequencies, making the output
    suitable for waveform comparisons and matched-filter SNR calculations.

    For SNR calculations, use the PSD returned by `get_psd()`.

    Example
    -------
    >>> waveform_frequencies = np.logspace(-4, -1, 500)
    >>> lisa = LISASensitivityFromWaveform(
    ...     waveform_frequencies,
    ...     observation_time="4yr",
    ... )
    >>> frequencies, noise_psd = lisa.get_psd()
    """

    def __init__(
        self,
        frequencies: ArrayLike,
        observation_time: str = "1yr",
    ) -> None:
        super().__init__(
            frequencies=frequencies,
            observation_time=observation_time,
        )


# ---------------------------------------------------------------------------
# Standalone LISA sensitivity-curve interface
# ---------------------------------------------------------------------------
class LISASensitivity(_LISANoiseModel):
    """
    Generate a standalone LISA sensitivity curve.

    This class creates a logarithmically spaced frequency grid internally
    and evaluates the LISA noise model over the selected frequency range.
    It is useful for quickly plotting, inspecting, or exporting the expected
    LISA sensitivity without supplying a waveform frequency array.

    Example
    -------
    >>> lisa = LISASensitivity(observation_time="4yr")
    >>> lisa.plot(quantity="asd", show_components=True)
    """

    def __init__(
        self,
        observation_time: str = "1yr",
        minimum_frequency: float = 1.0e-5,
        maximum_frequency: float = 1.0,
        number_of_frequencies: int = 1000,
    ) -> None:
        if minimum_frequency <= 0.0:
            raise ValueError(
                "minimum_frequency must be greater than zero."
            )

        if maximum_frequency <= minimum_frequency:
            raise ValueError(
                "maximum_frequency must be greater than "
                "minimum_frequency."
            )

        if number_of_frequencies < 2:
            raise ValueError(
                "number_of_frequencies must be at least 2."
            )

        frequencies = np.logspace(
            np.log10(minimum_frequency),
            np.log10(maximum_frequency),
            number_of_frequencies,
        )

        super().__init__(
            frequencies=frequencies,
            observation_time=observation_time,
        )