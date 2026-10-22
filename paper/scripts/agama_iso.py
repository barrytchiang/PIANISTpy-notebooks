import numpy as np
import agama

print("Step 1: Initializing AGAMA in default physical units...")
agama.setUnits(length=1.0, mass=1.0, velocity=1.0)
print(f"  -> Default units active. Internal G = {agama.G:.10e}")

# Scale parameters
rho_0 = 1.0
r_scale = 1.0
nfw_mass = 4.0 * np.pi * rho_0 * (r_scale ** 3)

# Baseline analytical formula container
dens_analytical = agama.Density(type="NFW", mass=nfw_mass, scaleRadius=r_scale)

print("\nStep 2: Building purely numeric 1D grid-interpolated splines via Multipole (lmax=0)...")
# FIX: Use type="Multipole" with lmax=0 to build a purely spherical radial spline grid.
pot_numeric = agama.Potential(
    type="Multipole", 
    density=dens_analytical, 
    lmax=0, 
)

print("Step 3: Computing Numerical DF over the interpolated grid potential...")
# Pass pot_numeric as both potential and density to ensure perfect numerical alignment
df_numeric = agama.DistributionFunction(type="QuasiSpherical", density=pot_numeric, potential=pot_numeric)

print("Step 4: Setting up evaluation grid (10,000 steps)...")
radii = np.logspace(-9.0, 10.0, int(1e4), dtype=np.float64)

pos_matrix = np.zeros((len(radii), 3), dtype=np.float64, order="C")
pos_matrix[:, 0] = radii
# Evaluate potential values using the purely numerical spline object
pot_vals = pot_numeric.potential(pos_matrix)

print("Step 5: Converting 6D phase-space coordinates to orbital actions...")
phase_space_6d = np.zeros((len(radii), 6), dtype=np.float64, order="C")
phase_space_6d[:, :3] = pos_matrix  # Stationary coordinates at rest (v=0)

# Extract orbital actions numerically based strictly on the spline potential field table
af = agama.ActionFinder(pot_numeric)
actions_matrix = af(phase_space_6d)

print("Step 6: Evaluating DF using the derived numeric actions...")
df_raw = df_numeric(actions_matrix)

print("Step 7: Executing post-calculation unit conversion...")
psi_0 = 4.0 * np.pi * agama.G * rho_0 * (r_scale ** 2)
Z_dimensionless = -pot_vals / psi_0
df_vals = df_raw * ((4.0 * np.pi * agama.G) ** 1.5) * (r_scale ** 3) * (rho_0 ** 0.5)

print("Step 8: Computing density profiles natively via an AGAMA GalaxyModel...")
galaxy_model = agama.GalaxyModel(pot_numeric, df_numeric)
rho_vals = galaxy_model.moments(pos_matrix, dens=True, vel=False, vel2=False)

# Sample the numerical potential's inherent density profile to track true self-consistent errors
rho_baseline = dens_analytical.density(pos_matrix)
rho_relative_diff = (rho_vals - rho_baseline) / rho_baseline

print("Step 9: Compiling matrix results and writing text file...")
output_data = np.column_stack((radii, Z_dimensionless, df_vals, rho_vals, rho_relative_diff))
output_file = "agama_numerical_iso.txt"

columns = ["Radius(r_scale)", "Relative_Energy", "Raw_DF(Normalized)", "Rho(rho_0)", "Fractional_Error"]
header_string = "".join(f"{col:<26}" for col in columns)

np.savetxt(
    output_file, 
    output_data, 
    fmt="%-26.18e", 
    header=header_string, 
    comments=""
)

print(f"[Success] Fully self-consistent numerical AGAMA profile dataset written to: {output_file}")
