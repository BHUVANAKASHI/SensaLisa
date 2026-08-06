# Validation

## Software validation

The package has been tested on:

- Ubuntu 24.04
- Python 3.11
- Python 3.12

The automated test suite verifies

- PSD generation
- ASD generation
- Characteristic strain
- Waveform-frequency interface
- Invalid input handling
- Plot generation

Run the tests with

```bash
python -m pytest -v
