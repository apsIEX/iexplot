# Changelog

## 2026-08-12 — k-space (angle→momentum) conversion fixes

Fixed three bugs in the angle→momentum (k-space) mapping code and added a
user-facing wrapper so an angle/angle/energy cube can be converted to
kx/ky/energy directly from loaded data.

### New

- **`IEXnData.stack_mdaEA_kmap(*scanNum, BE=True, **kwargs)`**
  (`iexplot/IEX_pkg/Plot_EA.py`)
  k-space counterpart of `stack_mdaEA`. Loads the same `EA_list` via
  `make_EA_list` and returns a momentum-space volume `x: kx, y: ky, z: BE/KE`
  from a thetaX (polar) scan. Accepts the usual `make_EA_list` kwargs
  (`EAnum`, `EAavg`, …) plus the alignment offsets below.

  ```python
  cube = iex.stack_mdaEA_kmap(scanNum, BE=True)          # single Fermi-map scan
  cube = iex.stack_mdaEA_kmap('mda', start, stop, 1)     # series of mda scans
  cube = iex.stack_mdaEA_kmap(scanNum, BE=True,
                              slit_offset=2.0,            # deg on slit angle -> ky
                              thetaX_offset=-1.0,         # deg on polar angle -> kx
                              E_offset=0.35)              # eV Fermi level on BE axis
  ```

- **Alignment offsets** on `kmap_scan_thetaX` / `stack_mdaEA_kmap`. Each enters
  the conversion at exactly one place:
  - `slit_offset` (deg) — added to the slit angle (thetaY / angScale) before
    `theta_to_ky`; corrects the slit-angle zero.
  - `thetaX_offset` (deg) — added to the polar (thetaX) angle before
    `theta_to_kx`/`theta_to_ky`; corrects the manipulator zero.
  - `E_offset` (eV, scalar or one per slice) — Fermi-level offset on the
    Binding-Energy axis (`BE = hv + E_offset - wk - KE`); a per-slice array
    regrids each slice onto a common BE grid to align a drifting Fermi level.
    Affects the energy axis only, not k.
  - `KE_offset` (eV, scalar or one per slice) — added to KE *in the k-formula
    only* (momentum-magnitude / drift correction); does not move the energy
    axis.

### Fixed

- **`kmap_scan_thetaX`** (`iexplot/pynData/pynData_ARPES.py`) — signature and
  behavior changed. It previously took a pre-stacked `EAstack` and passed a raw
  `numpy` slice (`EAstack.data[:,:,0]`) to `kmapping_boundaries_slice`, which
  expects a `pynData_ARPES` object → `AttributeError`; it also read scalar
  metadata (`hv`, `wk`, …) off the stacked cube where those attributes are
  per-slice lists.
  It now takes **`EA_list`** (the list of EA objects, e.g. from
  `make_EA_list`), builds the kx range across **all** slices, converts the slit
  angle to ky per energy row via `ARPES_angle_k`, and returns a shape-consistent
  `nData` (`x: kx, y: ky, z: BE/KE`). Signature:
  `kmap_scan_thetaX(EA_list, BE=True, **kwargs)`.

- **`kmapping_boundaries_slice`** (`iexplot/pynData/pynData_ARPES.py`,
  slitDir `'H'` branch) — `thetaX_max` used `np.min(EA.angScale)` (copy-paste of
  `thetaX_min`), collapsing the kx range to zero width. Now uses `np.max`.

- **`kmapping_stack`** (`iexplot/pynData/pynData_ARPES.py`) — referenced an
  undefined `E_unit` before assignment → `NameError` on every call. Energy mode
  is now selected from the `BE` flag (`if not BE: … else: …`), the redundant
  `min(KE_to_BE(KE_min…), KE_to_BE(KE_min…))` was reduced to a single call, and
  the loop's hardcoded `EA_Escale(EA, BE=True, …)` now honors the `BE` argument.

### Known limitations / not addressed

- `kmap_scan_thetaX` supports **`slitDir='V'`** polar scans only (raises
  `NotImplementedError` otherwise). The kx axis is a linear range over the polar
  extent (near-normal-emission approximation); the ky axis is converted per
  energy. Validate against real data before quantitative use.
- `kmapping_stack` no longer crashes, but still has pre-existing logic bugs
  independent of the `NameError`: the KE branch's `np.arange` step
  (`abs(BE_min-BE_max)`) collapses the energy axis to ~1 point, and the final
  `updateAx` reports a dimension mismatch in BE mode. These were out of scope
  for this change. Prefer `kmap_scan_thetaX` / `stack_mdaEA_kmap`.
