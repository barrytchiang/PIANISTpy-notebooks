# Reproducing the paper

One notebook per figure family of the paper (Chiang, van den Bosch and Schive 2026), added with the 1.0.0
release. Each notebook names the figures it reproduces, the release it was run with, the models it builds (with
their identities and seeds) and the measured numbers the figure captions quote. The two illustrations of the
paper (the truncation sketch and the projection sketch) are drawings and have no notebook.

| Notebook | Figures | What it builds |
|---|---|---|
| `distribution_functions.ipynb` | the untruncated distribution functions; Method I truncation; Method II truncation | NFW c = 10 models of every anisotropy family: the anisotropy and the distribution function against radius and energy; the truncated distribution functions and densities; the Method II children and their dispersions |
| `superposition.ipynb` | the superposed anisotropy profiles; the fit of an anisotropy profile over the superposition weights | Method II children of one truncated parent superposed with positive weights; the particle draws binned in radius; the fit over the weights at a fixed truncated potential (NumPyro NUTS) with the per-model cost line |
| `benchmark_isotropic_nfw.ipynb` | the round-trip benchmark of the untruncated isotropic NFW model | the inversion's distribution function and the density recovered from it against the closed forms |
| `observables.ipynb` | the local velocity distributions in shells; the line-of-sight dispersion profiles and their aperture averages; the line-of-sight velocity distributions | a truncated NFW c = 30 model in four anisotropy families: the velocity distribution at three radii, the dispersion profiles, the circular apertures centered and offset, the line-of-sight distributions |
| `appendix_tables.ipynb` | the distribution-function comparison and the cumulative-distribution comparison of the appendix | the Method II children at several constant anisotropies on one parent; the sampler's speed tables and their inverse |
| `nbody_isolation.ipynb` | the isolation runs: the particle distribution in time, the enclosed radii, the varying-anisotropy montage, the triaxiality | reads the GAMER runs' reduced outputs (the runs themselves are not rerun by the notebook) and draws the figures; the initial conditions are built here from the released package |

The N-body figures depend on simulation runs made outside the package; the notebook rebuilds their initial
conditions and reads the runs' reduced data, which is stored beside it.
