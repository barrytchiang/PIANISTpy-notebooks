import numpy as np
import warnings
from galpy.potential import NFWPotential, interpSphericalPotential
from galpy.df import eddingtondf

# Set standard code units: G = rho_0 = r_scale = 1
G, rho_0, r_scale = 1.0, 1.0, 1.0
nfw_amp = 4.0 * np.pi * G * rho_0 * (r_scale ** 3)

print("Step 1: Generating baseline analytical profile...")
nfw_base = NFWPotential(amp=nfw_amp, a=r_scale)

print("Step 2: Building pure numerical potential via interpSphericalPotential...")
poisson_r_grid = np.logspace(-10.0, 10.0, int(1e5), dtype=np.float64)
interp_pot = interpSphericalPotential(rforce=nfw_base, rgrid=poisson_r_grid)
#interp_pot = interpSphericalPotential(rforce=nfw_base, rgrid=poisson_r_grid, interpInf=True)

print("Step 3: Initializing Eddington DF...")
df_numeric = eddingtondf(pot=interp_pot, denspot=nfw_base)

print("Step 4: Setting up evaluation grid (1000 steps)...")
radii = np.logspace(-9.9, 9.9, int(1e3), dtype=np.float64)

# Evaluate the numerical potential across the radial array
pot_vals = interp_pot(radii, np.zeros_like(radii))

# FIX 1: Completely remove the velocity buffer to evaluate strictly at rest (v=0)
E_bound = pot_vals

print("Step 5: Executing vectorized raw DF numerical evaluation...")
try:
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        df_raw = df_numeric.fE(E_bound)
    df_val = df_raw * ((4.0 * np.pi * G) ** 1.5) * (rho_0 ** 0.5) * (r_scale ** 3)
    df_val = np.nan_to_num(df_val, nan=0.0, posinf=0.0, neginf=0.0)
except Exception as e:
    df_val = np.zeros_like(radii)

print("Step 6: Executing analytical fitted DF evaluation (Lane 2022)...")
def F_NFW_iso_Lane2022(Z):
    safe_Z = np.clip(Z, 1e-10, 1.0 - 1e-10)
    E2 = 1.0 - safe_Z
    poly = (0.0926081086527954 + 0.0232272797489981 * safe_Z + 0.258346829924101 * safe_Z**2.0 - 
            2.97848277491979 * safe_Z**3.0 + 14.9776586391246 * safe_Z**4.0 - 46.6587221550258 * safe_Z**5.0 + 
            92.6397009471828 * safe_Z**6.0 - 117.647787290798 * safe_Z**7.0 + 92.5144063082258 * safe_Z**8.0 - 
            41.0268009529576 * safe_Z**9.0 + 7.84806318891231 * safe_Z**10.0)
    val = (safe_Z**1.5 / E2**2.5) * (-np.log(safe_Z) / E2)**(-2.75) * poly
    return np.where((Z > 0.0) & (Z < 1.0), val, 0.0)

# FIX 2: Compute the true analytical dimensionless relative energy profile Z for an untruncated NFW
# This ensures perfect boundary scaling and removes any numerical spline extrapolation noise
x = radii / r_scale
Z_dimensionless = np.log1p(x) / x

df_fitted = F_NFW_iso_Lane2022(Z_dimensionless)

print("Step 7: Computing relative deviations...")
relative_derivation = np.where(df_fitted > 0.0, (df_val - df_fitted) / df_fitted, 0.0)

# Export configuration
output_data = np.column_stack((radii, Z_dimensionless, df_val, df_fitted, relative_derivation))
output_file = "galpy_numerical_iso.txt"

columns = ["Radius(r_scale)", "Relative_Energy", "Raw_DF(Normalized)", "Fitted_DF(Lane2022)", "Relative_Derivation"]
header_string = "".join(f"{col:<26}" for col in columns)

np.savetxt(output_file, output_data, fmt="%-26.18e", header=header_string, comments="")
print(f"\n[Success] Execution complete. Formatted matrix written to: {output_file}")
