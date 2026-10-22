# PIANISTpy notebooks

Jupyter notebooks for [PIANISTpy](https://github.com/barrytchiang/PIANISTpy): two tutorials, and the notebooks that
reproduce the result figures of
[Chiang, van den Bosch and Schive (2026d), MNRAS submitted, arXiv:2610.28758](https://arxiv.org/abs/2610.28758), henceforth Chiang+(2026d). Every
notebook is stored with its outputs from PIANISTpy ver. 1.0.0, and the
[Examples](https://pianistpy.com/docs/notebooks/) pages of the website show each one.

## Running a notebook

`pip install -r requirements.txt` installs PIANISTpy ver. 1.0.0 and the other packages the notebooks use. Each
notebook computes every number and figure it shows in its own cells. The tutorials run on a laptop; the first cell
of each figure notebook states its run time on one 32-core node, from about 2 minutes to about two hours.

## Notebooks

| Notebook | Content |
|---|---|
| `tutorials/particles.ipynb` | Particle initial conditions drawn from an analytic Hernquist model, the enclosed mass against the closed form, and a file written and read back |
| `tutorials/observables.ipynb` | Line-of-sight velocity dispersions at projected radii and over apertures, also in physical units |
| `paper/fig04_05_06.ipynb` | Figs. 4, 5 and 6 of Chiang+(2026d): distribution functions with and without truncation |
| `paper/fig07.ipynb` | Fig. 7: anisotropy profiles from linear superposition |
| `paper/fig08.ipynb` | Fig. 8: isotropic NFW benchmark against other codes |
| `paper/fig13_15_16.ipynb` | Figs. 13, 15 and 16: velocity distributions and observables |
| `paper/figC1_C2.ipynb` | Figs. C1 and C2: distribution function and velocity distribution accuracy checks |

The scripts and layout files under `paper/scripts/` and `paper/data/` are the figure notebooks' plotting code and
the page layouts of the published Figs. 4 to 6; they hold no computed values.

## License

BSD 3-Clause, as the package; see `LICENSE`.
