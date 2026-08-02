# SensaLisa

**SensaLisa** is a lightweight, user-friendly Python toolkit for generating and visualizing sensitivity curves for the Laser Interferometer Space Antenna (LISA).

Designed for both gravitational-wave researchers and students, SensaLisa provides an intuitive interface for computing detector sensitivity without requiring extensive setup or familiarity with the underlying implementation.

---

## Features

- Generate LISA sensitivity curves with minimal code.
- Fast and lightweight implementation.
- Simple, intuitive API designed for research workflows.
- Publication-quality plots with customizable visualization.
- Modular design for easy integration into existing analysis pipelines.
- Suitable for education, rapid prototyping, and scientific research.

---

## Why SensaLisa?

Many sensitivity curve implementations are embedded inside larger software packages or require unnecessary setup for simple analyses.

SensaLisa focuses on one objective:

> **Making LISA sensitivity calculations simple, transparent, and accessible.**

Whether you are exploring detector performance, testing waveform models, or preparing figures for a publication, SensaLisa allows you to generate sensitivity curves in just a few lines of code.

---

## Installation

```bash
git clone https://github.com/BHUVANAKASHI/SensaLisa.git

cd SensaLisa

pip install -r requirements.txt
```

or install directly from source

```bash
pip install .
```

---

## Quick Start

```python
from sensalisa import ...

# Example code here
```

Generate a LISA sensitivity curve with only a few commands.

---

## Applications

SensaLisa can be used for

- LISA sensitivity studies
- Signal-to-noise ratio calculations
- Gravitational-wave data analysis
- Detector performance visualization
- Research and teaching

---

## Citation

If SensaLisa contributes to your research, please cite the repository and any accompanying publication.

```bibtex
@software{SensaLisa,
  author = {Bhuvaneshwari Kashi},
  title  = {SensaLisa: A User-Friendly Toolkit for LISA Sensitivity Curves},
  year   = {2024},
  url    = {https://github.com/BHUVANAKASHI/SensaLisa}
}
```

---

## Contributing

Contributions, feature requests, and bug reports are welcome.

Please open an Issue or submit a Pull Request.

---

## Acknowledgements

SensaLisa is inspired by and partially adapts components from the LISA_Sensitivity toolkit developed by the eXtreme Gravity Institute. We gratefully acknowledge the original authors for their implementation of the LISA sensitivity model and their contribution to the gravitational-wave community.

SensaLisa extends this foundation by providing a streamlined, user-friendly interface, simplified workflows, and enhanced visualisation tools for generating and exploring LISA sensitivity curves.

## License

This project is released under the MIT License.

## References

This project builds upon the following work:

- Robson, T., Cornish, N. J., & Liu, C. (2019). *The construction and use of LISA sensitivity curves*. Classical and Quantum Gravity, 36(10), 105011.
- LISA_Sensitivity Toolkit: https://github.com/eXtremeGravityInstitute/LISA_Sensitivity
