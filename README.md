# PIANISTpy notebooks

Tutorials and the notebooks that reproduce the result figures of the PIANISTpy initial release paper, [Chiang, van den Bosch and Schive (2026d), MNRAS](https://pianistpy.com/docs/project/citing), submitted (henceforth [Chiang+(2026d)](https://pianistpy.com/docs/project/citing)). Every notebook is stored with its
outputs and was run against the PIANISTpy release named below; the documentation site at
[pianistpy.com](https://pianistpy.com) renders them as pages of its manual.

The package itself is [PIANISTpy](https://github.com/barrytchiang/PIANISTpy); install it with
`pip install pianistpy` before running a notebook.

## Release

These notebooks were run with PIANISTpy ver. 0.9.0 (a pre-release). They are rerun and committed again with each
release; the development branch of the package may be ahead of them.

## Index

### Tutorials (`tutorials/`)

| Notebook | What it shows |
|---|---|
| `tutorials/particles.ipynb` | A sampler on an analytic Hernquist model: the draw, the enclosed mass against the closed form, a file written and read back |
| `tutorials/observables.ipynb` | Line-of-sight dispersions at projected radii and over apertures, a prepared table, the same in physical units |

Planned for ver. 1.0.0: a truncated model (profile to distribution function to model, Method I and Method II);
superposition and inference; an aperture of arbitrary geometry.

### Reproducing Chiang+(2026d) (`paper/`)

One notebook per figure family of [Chiang+(2026d)](https://pianistpy.com/docs/project/citing), released with ver. 0.9.9: the distribution-function panels;
the superposition figures with the fit of an anisotropy profile over the superposition weights; the observable
mocks; the appendix figures.

## Running a notebook

Each notebook's first cell states the package version and the extra packages it needs beyond PIANISTpy. The
figure notebooks build their models on a compute node; the tutorials run on a laptop.

## License

BSD 3-Clause, as the package; see `LICENSE`.
