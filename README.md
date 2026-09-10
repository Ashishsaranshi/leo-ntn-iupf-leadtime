# LEO-NTN I-UPF Relocation Lead-Time — Evaluation Artifact

This repository contains the evaluation and reproducibility artifacts
accompanying the paper on **I-UPF relocation lead-time in LEO
Non-Terrestrial Networks (LEO-NTNs)**.

The artifact provides:

- the script used to generate the system/timing-budget figure;
- the ephemeris-driven evaluation script;
- the TLE snapshots used for the constellation evaluation;
- satellite visibility and pass calculations;
- propagation-delay and RTT calculations;
- relocation lead-time and usable-margin calculations; and
- batch and M/G/1 processing-feasibility calculations.

The purpose of this repository is to make the numerical evaluation in the
paper independently reproducible from the supplied code, assumptions, and
TLE snapshots.

---

## Repository contents

| File               | Description                                                               |
|--------------------|---------------------------------------------------------------------------|
| `fig1.py`          | Generates the system architecture and relocation timing-budget figure.    |
| `sim_figs.py`      | Main ephemeris-driven evaluation pipeline used for the numerical results. |
| `starlink.txt`     | TLE snapshot used for the Starlink-550 evaluation.                        |
| `iridium.txt`      | TLE snapshot used for the Iridium-780 evaluation.                         |
| `oneweb.txt`       | TLE snapshot used for the OneWeb-1200 evaluation.                         |
| `README.md`        | This reproducibility guide.                                               |
| `requirements.txt` | Python package dependencies.                                              |

---

## Software requirements

- Python 3
- NumPy
- Matplotlib
- Skyfield

Install the dependencies with:

```bash
python3 -m pip install -r requirements.txt

#Run command for sim_figs.py:
python3 sim_figs.py --starlink starlink.txt --iridium iridium.txt --oneweb oneweb.txt


#Run command for fig1.py:
python3 fig1.py


