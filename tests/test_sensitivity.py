import numpy as np
import pytest

from SensaLisa import (
    LISASensitivity,
    LISASensitivityFromWaveform,
)


def test_standalone_sensitivity():
    """Standalone model should return valid, increasing frequency and PSD arrays."""
    lisa = LISASensitivity(
        observation_time="4yr",
        minimum_frequency=1e-5,
        maximum_frequency=1.0,
        number_of_frequencies=1000,
    )

    frequencies, psd = lisa.get_psd()

    assert frequencies.shape == (1000,)
    assert psd.shape == frequencies.shape
    assert np.all(np.diff(frequencies) > 0)
    assert np.all(np.isfinite(psd))
    assert np.all(psd > 0)


def test_waveform_frequencies_are_preserved():
    """Waveform interface should preserve the supplied frequency array."""
    waveform_frequencies = np.logspace(-4, -1, 500)

    lisa = LISASensitivityFromWaveform(
        frequencies=waveform_frequencies,
        observation_time="4yr",
    )

    returned_frequencies, psd = lisa.get_psd()

    assert np.array_equal(
        returned_frequencies,
        waveform_frequencies,
    )
    assert psd.shape == waveform_frequencies.shape
    assert np.all(np.isfinite(psd))
    assert np.all(psd > 0)


def test_asd_matches_psd():
    """ASD should equal the square root of the PSD."""
    lisa = LISASensitivity(observation_time="1yr")

    _, psd = lisa.get_psd()
    _, asd = lisa.get_asd()

    assert np.allclose(
        asd,
        np.sqrt(psd),
    )


def test_characteristic_strain_matches_definition():
    """Characteristic strain should equal sqrt(frequency * PSD)."""
    lisa = LISASensitivity(observation_time="2yr")

    frequencies, psd = lisa.get_psd()
    _, characteristic_strain = lisa.get_characteristic_strain()

    assert np.allclose(
        characteristic_strain,
        np.sqrt(frequencies * psd),
    )


def test_both_interfaces_agree():
    """Both interfaces should return identical noise at identical frequencies."""
    standalone = LISASensitivity(
        observation_time="4yr",
        minimum_frequency=1e-5,
        maximum_frequency=1.0,
        number_of_frequencies=500,
    )

    frequencies, standalone_psd = standalone.get_psd()

    waveform_model = LISASensitivityFromWaveform(
        frequencies=frequencies,
        observation_time="4yr",
    )

    returned_frequencies, waveform_psd = waveform_model.get_psd()

    assert np.array_equal(
        returned_frequencies,
        frequencies,
    )
    assert np.allclose(
        waveform_psd,
        standalone_psd,
        rtol=1e-12,
        atol=0.0,
    )


@pytest.mark.parametrize(
    "invalid_frequencies",
    [
        np.array([]),
        np.array([0.0, 1e-3]),
        np.array([-1e-4, 1e-3]),
        np.array([1e-4, np.nan]),
        np.array([1e-4, np.inf]),
        np.array([[1e-4, 1e-3]]),
    ],
)
def test_invalid_frequencies_raise_value_error(
    invalid_frequencies,
):
    """Invalid frequency arrays should raise ValueError."""
    with pytest.raises(ValueError):
        LISASensitivityFromWaveform(
            frequencies=invalid_frequencies,
        )


def test_invalid_observation_time():
    """Unsupported observation times should raise ValueError."""
    with pytest.raises(ValueError):
        LISASensitivity(
            observation_time="10yr",
        )


def test_plot_is_saved(tmp_path):
    """Plotting with save_fig=True should create a non-empty file."""
    output_file = tmp_path / "lisa_test_plot.png"

    lisa = LISASensitivity(observation_time="1yr")

    lisa.plot(
        quantity="asd",
        show_components=True,
        save_fig=True,
        filename=str(output_file),
    )

    assert output_file.exists()
    assert output_file.stat().st_size > 0
