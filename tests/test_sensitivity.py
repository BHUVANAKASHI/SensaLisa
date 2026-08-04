import numpy as np

from SensaLisa import (
    LISASensitivity,
    LISASensitivityFromWaveform,
)


def test_standalone_sensitivity():
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
    waveform_frequencies = np.logspace(-4, -1, 500)

    lisa = LISASensitivityFromWaveform(
        frequencies=waveform_frequencies,
        observation_time="4yr",
    )

    returned_frequencies, psd = lisa.get_psd()

    assert np.allclose(
        returned_frequencies,
        waveform_frequencies,
    )
    assert psd.shape == waveform_frequencies.shape
    assert np.all(np.isfinite(psd))
    assert np.all(psd > 0)


def test_asd_matches_psd():
    lisa = LISASensitivity(observation_time="1yr")

    _, psd = lisa.get_psd()
    _, asd = lisa.get_asd()

    assert np.allclose(asd, np.sqrt(psd))
