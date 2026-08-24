# iexplot — Package Review

Whole-package static review (read-only) of the `iexplot/` source tree (40 modules, ~13.8k LOC).
Findings are verified against source. Severity: **high** = crashes / silently wrong results on a
reachable path; **med** = wrong on edge/error paths or misleading; **low** = minor / cosmetic.

> Generated from a 6-way parallel review. Companion index: `.iexplot_index.json` / `PACKAGE_INDEX.md`.

## Area health at a glance

| Area | Health | Notes |
|------|--------|-------|
| `spec_write/` | **broken** | All 3 modules non-functional (syntax error, missing return, undefined names, no `__init__.py`) |
| `pynData/` core | poor–fair | Happy path works; `save()`/`nAppend()`/k-mapping broken; `mdaUtils.py` is dead duplicate |
| `pynData/` fit/img/plot | fair | `'step:'` key typo, `plot_nd_avg` ignores args, ROI helpers triplicated |
| `IEX_pkg/` | fair | Common path OK; `make_EA_list`/`EA_nd`/`IEX_nData` AD-key bugs |
| root modules | fair | A few return-None / import bugs; heavy duplicated boilerplate |
| `mda/` + `mda_quick_plot` | fair | Legacy Py2 remnants in verbose/write paths; pervasive `except: pass` |

---

## Systemic patterns (fix these as classes, not one-offs)

1. **Bare `except:` masking real bugs.** Dozens of sites (`spec_write/*`, `mda_quick_plot.py`, `pynData.py:506`, `nmda.py:171`, `video_utilities.py:32`, `Plot_MDA.py`). These swallow the undefined-name / wrong-arg bugs below, turning crashes into silent blank output. Replace with `except Exception as e:` that at minimum logs, and scope narrowly.
2. **Computed-but-never-returned/assigned.** Recurring correctness class: `Plot_EA.make_EA_list:410` (`img/len(...)`), `constants_conversions.T_K2meV:10`, `fitting._shirley:400`, `plotting.plot_3D` (return commented out), `pynData_plot`/`fit_mda_*` (no return), `fit1D.py:221` (`swapaxes` not assigned), `pynData.py:596` (`list.append` returns None).
3. **Wrong-key guards / mismatched dict keys.** `plotting.py:119` (`'profiles'` vs `'profile'`), `pynData_fitting.py:35` (`'step:'`), `IEX_nData.py:163` (`'ADtype'` vs `'AD_key'`), `pynData.py:244` (`crop_x` coord/index).
4. **`type(x)==T` / `== None` instead of `isinstance` / `is`.** Misses numpy scalar types and is always-False in places: `pynData.py:442`, `pynData_imgProc.py:329`, `utilities.make_num_list`, `Plot_MCA`, several `!= None`.
5. **Positional/keyword call mismatches.** `mda_quick_plot` `EA_EDC`/`EA_metadata`/`nc_unpack`, `Plot_MDA.mda_detector(ax=...)`, error handlers calling helpers with wrong args (`Plot_MDA.py:61/94`).
6. **Python-2 remnants (Py3-incompatible) in `mda/mda.py`.** `has_key`, `string.upper`, `map()`-as-list, `tkFileDialog`, `for i in len(...)`. Confined to verbose/write/op paths, so default `readMDA(useNumpy=True)` still works.
7. **Large-scale duplication.** `pynData/mdaUtils.py` is a full dead copy of `mda/mda.py`; `spec_write` Kappa≈Octuople; ROI helpers in 3 files; `crop_x/y/z`; fit initial-guess blocks; `scanDim` family.

---

## BUGS — high severity (reachable crash or silently wrong result)

### spec_write (entire subpackage non-functional)
- `iexplot/spec_write/Kappa_spec_file.py:24` — `kwargs.setdefault('suffix_format':'{:04}.mda')` uses `:` not `,` → **SyntaxError**, module can't import.
- `iexplot/spec_write/Kappa_spec_file.py:27-30` — references bare `prefix`/`suffix_format` never assigned (only `kwargs['prefix']` exists) → NameError even after the syntax fix.
- `iexplot/spec_write/Octuople_spec_file.py:30` — `Octupole_get_data` has no `return`; returns `None`, so every caller (`data[0]`, `data[1]`) raises TypeError.
- `iexplot/spec_write/Octuople_spec_file.py:149-150` — `kwargs('prefix',...)` calls the dict as a function → TypeError (should be `.setdefault`).
- `iexplot/spec_write/mda_to_spec.py:39,53,58,62,69,71,113,120,122` — cascade of undefined names (`kwargs`, `sf`, `scanNum`, `Scantype`, `Kappa`, `find_detectors`, `endstation`) → NameError; `MakeSpecFile`/`UpdateSpecFile` cannot run.
- `iexplot/spec_write/` — **no `__init__.py`**, so the subpackage isn't importable.

### pynData core
- `iexplot/pynData/pynData.py:197` — `h.create_grsaveoup('scale')` typo for `create_group`; `nData.save()` always raises AttributeError.
- `iexplot/pynData/pynData.py:554,562,570` — `np.ddstack`/`np.hdstack`/`np.vdstack` don't exist; `nAppend` raises on every axis.
- `iexplot/pynData/pynData.py:244` — `crop_x` sets `index` default but reads `kwargs['coord']` → KeyError (inverted vs crop_y/crop_z).
- `iexplot/pynData/pynData.py:206` — `if len(self.extras[0]) != 0:` indexes a dict with int `0` → KeyError; extras never saved.
- `iexplot/pynData/pynData.py:442` — `if type(dstack_scale) == None:` always False (should be `is None`); default-scale branch dead.
- `iexplot/pynData/pynData_ARPES.py:489` — `E_unit` used before assignment in `kmapping_stack` → NameError.
- `iexplot/pynData/pynData_ARPES.py:401` — `nARPES.kScale(...)` method doesn't exist → AttributeError in `kmap_scan_hv`.
- `iexplot/pynData/pynData_ARPES.py:560` — `nData_h5Group_w(nd.EDC,g,"MDC")` writes EDC under the MDC group; MDC never saved.
- `iexplot/pynData/pynData_ARPES.py:425` — `np.min(EA.angScale)` should be `np.max` for slitDir 'H'; kx range collapses to zero.
- `iexplot/pynData/nmda.py:171` — `except: e=1` (print commented out) swallows all read errors → silently empty nmda.
- `iexplot/pynData/nmda.py:194` — `if key in self.det[key]:` membership on an nData object → TypeError; `setScaleDet` broken.

### pynData fit/img/plot
- `iexplot/pynData/pynData_fitting.py:35,81` — fit_funcs key is `'step:'` (stray colon) but callers pass `'step'`; step fits never resolve.
- `iexplot/pynData/pynData_plot.py:97` — `plot_nd_avg` hard-codes `nd_avg(...,ax='y',Cen=nan,WidthPix=nan)`, ignoring user args; never bins where asked.
- `iexplot/pynData/pynData_fitting.py:38,84` — `print('...'+list(...))` str+list → TypeError; the error message itself crashes.

### IEX_pkg
- `iexplot/IEX_pkg/Plot_EA.py:410` — `img/len(EAlist)` discards the average; `EA.data = img` stores the raw sum. `EAavg=True` returns a **sum, not an average**.
- `iexplot/IEX_pkg/IEX_nData.py:170` — ARPES `AD_key="EA"` then an `if/else` overwrites it with `'AD'` (should be `elif`); ARPES mdaAD loads under wrong key.
- `iexplot/IEX_pkg/IEX_nData.py:163` — guard checks `'ADtype' in kwargs` but reads `kwargs['AD_key']`; docstring says `AD_type` — three-way mismatch.
- `iexplot/IEX_pkg/Plot_EA.py:57` — `_sum_EAs` does `make_num_list(*EAnum)`; a discrete list `[1,3,4]` becomes range `(1,3,4)` → wrong EAs summed.
- `iexplot/IEX_pkg/Plot_EA.py:35` — `elif self.dtype == "mdaEA" or "mdaAD":` is always True; combined with bare `except` (line 38) `EA` can be unbound.
- `iexplot/IEX_pkg/Plot_EA.py:445` — index branch `stack_scale = stack_scale[-1]+1` replaces the array with a scalar / IndexErrors on first iteration.
- `iexplot/IEX_pkg/Plot_MDA.py:249,262` — `mda_detector(...,ax=...)` but `mda_detector(self,scanNum,detNum)` has no `ax` kwarg → TypeError.
- `iexplot/IEX_pkg/Plot_MDA.py:175` — `plot_mda` 2D with `row`/`column` falls through with no else → nothing plotted.
- `iexplot/IEX_pkg/Plot_MDA.py:390` — `mda_extra_pvs` `return d[key]` with `key` undefined (no loop entered) → NameError.

### root modules
- `iexplot/constants_conversions.py:10` — `T_K2meV` `return` returns nothing → None.
- `iexplot/constants_conversions.py:17` — `imfp` uses `sqrt(hv)` with no `sqrt` imported → NameError.
- `iexplot/plotting.py:119` — `if 'profiles' in kwargs and kwargs['profile']==True:` key mismatch → KeyError; profile branch unreachable.
- `iexplot/fitting.py:299` — `fit_poly` fits the full arrays, ignoring `xrange` (subrange only used for `x_fit`/`y_fit`); returned coefs don't match advertised fit.

### mda subsystem
- `iexplot/mda/mda.py:1008` — `EPICS_types_dict.has_key(n)` (Py2) → AttributeError on env-PV verbose read.
- `iexplot/mda_quick_plot.py:1291` — `nc_unpack` calls undefined `AD_path` (only `AD_filepath` imported) → NameError; breaks default-path netCDF loading.
- `iexplot/mda_quick_plot.py:1404,1411,1514-1515` — `EA_EDC`/`EA_metadata`/`plot_nc` pass too many positional args to `EA_spectra`/`nc_unpack` → TypeError.
- `iexplot/mda/mda.py:408` — `for i in len(data):` iterates an int → TypeError (`verboseData` nested-list branch).
- `iexplot/mda/mda.py:3180,3204,3230,3258` — `map(op,...)` stored as an iterator under Py3; `opMDA` output data unusable.

---

## BUGS — medium severity (edge/error paths, wrong labels, masked failures)

- `iexplot/pynData/pynData.py:596` — `d[key] = d[key].append(val_n)` sets value to None (append returns None).
- `iexplot/pynData/pynData.py:598` — `d[key] = d[key].list(val_n)` — lists have no `.list`.
- `iexplot/pynData/pynData.py:467` — `nData_list[i+1]` read at i==0; single/last element → IndexError in `ndstack`.
- `iexplot/pynData/pynData.py:581` — `.update({'nDataAppend',[...]})` passes a set → ValueError; also strings not arrays.
- `iexplot/pynData/pynData_ARPES.py:488` — `min(KE_to_BE(KE_min,...), KE_to_BE(KE_min,...))` — second should be `KE_max`; BE_max wrong.
- `iexplot/pynData/pynData_ARPES.py:380,406` — `new` reassigned to an interpolator then `.values` returns the untouched grid; interpolation never evaluated (k-map just transposes raw data).
- `iexplot/pynData/ARPES_functions.py:56` — `theta_to_kz` omits deg→rad and uses `cos` vs docstring `sin` (carries a "probably wrong" comment).
- `iexplot/pynData/nmda.py:170` — rank>3 calls `_setScale(axis='z')` twice; the `t` axis scale never set.
- `iexplot/pynData/nmda.py:345` — `hdict.update({key,...})` set literal → ValueError; header read broken.
- `iexplot/pynData/nmda.py:300,324` — stale leaked loop var `v`; iterates non-existent `nmda.EA` on save.
- `iexplot/pynData/nEA.py:148-149` — trailing commas make `filepath`/`prefix` 1-tuples, corrupting downstream string use.
- `iexplot/pynData/nEA.py:291` — netCDF header dict-comprehension iterates one variable using the last `key`; nonsensical header.
- `iexplot/pynData/pynData_plot.py:229` — image1 y-label set to `y2Unit`; wrong axis label when d1/d2 units differ.
- `iexplot/pynData/pynData_imgProc.py:56,309` — `crop`/`rotate3D` leave `d_c`/`d_rot` unbound on unhandled ax/dim → UnboundLocalError.
- `iexplot/pynData/fit1D.py:221,223` — `swapaxes` not assigned back in the `'y'` branch; results returned un-transposed.
- `iexplot/pynData/fit2D.py:233,235,241,243,308,310,316,318` — `np.argwhere(...)[-1,0]` with no match → IndexError.
- `iexplot/pynData/pynData_imgProc.py:329` — `type(nfold)==int` misses `np.int64`.
- `iexplot/pynData/pynData_plot.py:41` — `plot_nd` 1D branch drops `**kwargs` (Norm2One/offset/scale/xrange ignored).
- `iexplot/pynData/fit1D.py:121-122`, `fit2D.py:124-125` — chained-index pandas assignment (SettingWithCopy); use `.loc[key,'value']`.
- `iexplot/fitting.py:141` — Lorentzian FWHM uses the Gaussian factor `sqrt(8ln2)*sig`; should be `2*sig`.
- `iexplot/fitting.py:400,427` — `_shirley` returns None if it never converges; caller unpacks → TypeError.
- `iexplot/XAS_utilities.py:32,46` — `_Norm2Edge_index` leaves indices unassigned on bad input → UnboundLocalError at return.
- `iexplot/plotting.py:129` — `plot_2D` forwards `cbar`/`profiles` into `pcolormesh`, which rejects them.
- `iexplot/plotting.py:394` — `imageH` binning window uses wrong-axis width (`widthPix[1]` lower, `widthPix[0]` upper).
- `iexplot/utilities.py:36,55` — `make_num_list` rejects numpy scalars and `int(np.inf)` overflows when called directly.
- `iexplot/video_utilities.py:32` — bare `except:` on font resolution.
- `iexplot/IEX_pkg/Plot_MCA.py:37` — `plot_mca_avg` passes literal `Cen=nan,WidthPix=nan`, ignoring params.
- `iexplot/IEX_pkg/Plot_MDA.py:61,94` — except path calls `mda_positioners_list()` with no required `scanNum` → TypeError.
- `iexplot/IEX_pkg/Plot_MDA.py:672` — `mda_scan_summary` tests `'scanNum' in kwargs['pv_list']` (whole list) inside per-key loop.
- `iexplot/IEX_pkg/IEX_files_directories.py:42` — `CurrentPrefix` leaves `prefix` unbound for non-mda/EA dtypes → UnboundLocalError.
- `iexplot/IEX_pkg/Plot_AD.py:33,59` — `plot_ADmda`/`plot_AD` never forward `**kwargs` to `imshow`; cmap/vmin/vmax dropped.
- `iexplot/IEX_pkg/Plot_EA.py:187` — `fit_EDC` str+list concat and commented-out `return` → TypeError then KeyError.
- `iexplot/IEX_pkg/Plot_EA.py:399` — `sumEA=True` set but never read; `EAnum=inf` doesn't sum as documented.
- `iexplot/mda_quick_plot.py:217` — guard reads `'xrange'` but body sets `set_ylim(kwArg['yrange'])`.
- `iexplot/mda_kappa_plot.py:38,45,49` — `def fit_d4(scanNum=last_mda(), ...)` evaluates default once at import (stale scan).
- `iexplot/mda_quick_plot.py:631,612` — `fit_mda_*` never return; `round(None,2)` → TypeError (masked by try/except).
- `iexplot/mda/mda.py:2308,2464,1116,378` — 4D write append, `tkFileDialog` unimported, undefined `close`, `string.upper` (Py3).

---

## REDUNDANCIES

- `iexplot/pynData/mdaUtils.py` — **entire module is a dead duplicate** of `mda/mda.py` (`scanDim`/`scanPositioner`/`scanDetector`/`scanTrigger`, `readMDA`); imported nowhere. Delete or make it re-export.
- `iexplot/spec_write/Octuople_spec_file.py` — ~90% identical to `Kappa_spec_file.py`; parameterize into one module.
- `iexplot/spec_write/mda_to_spec.py:90` — `UpdateSpecFile` duplicates `MakeSpecFile`'s scan-write block verbatim.
- `iexplot/pynData/{fit1D,fit2D}.py` + `pynData_imgProc.py` — `_val_to_idx`/`_lim_to_bounds` triplicated (and `_val_to_idx` is unused/dead in all three).
- `iexplot/pynData/fit2D.py:288` — `guess_Lor2D` near-verbatim copy of `guess_Gauss2D`.
- `iexplot/pynData/pynData.py:232` — `crop_x/crop_y/crop_z` copy-paste; parameterize by axis (also fixes the `:244` kwargs bug).
- `iexplot/fitting.py:73+` — initial-guess boilerplate duplicated across `fit_gaussian/lorentzian/step/box`.
- `iexplot/plotting.py:242` — cursor/profile plotting duplicated between `plot_dimage` and `plot_3D`.
- `iexplot/mda_quick_plot.py:676+` — bytes-decode + `(0.0,0.0)`-trim boilerplate repeated across ~8 `mda_1D*`/`mda_2D` extractors; `SubplotsLayout` defined twice (157, 421); `plot_mda`≈`plot_mda_lists`.
- `iexplot/mda_kappa_plot.py:24` — kappa detector-number map duplicated in 3 places.
- `iexplot/utilities.py:101` — `take_closest_value` reimplements `find_closest`.
- `iexplot/pynData_fitting.py:30,76` — identical `fit_funcs` dict built twice.
- Unused-import blocks: `plotting.py:1` (`os`, `math *`, PIL, `cv2`), `fit1D/fit2D` large blocks, `spec_write/*` (`os,sys,glob,h5py,time,pandas`), `IEX_MCA.py`, `video_utilities.py:5`, `mda_quick_plot.py:8-9`.

---

## QoL suggestions

- **Adopt real error handling.** Ban blanket `except: pass`; log with context. This alone would surface most of the high bugs above.
- **Add a smoke-test / import test** that imports every module and calls `build_index.py` — would have caught the spec_write syntax error, the missing `sqrt`, and the return-None functions immediately. Consider CI + a linter (`ruff`/`flake8`) targeting F-codes (undefined names, unused imports) and `B006` (mutable defaults).
- `iexplot/pynData/pynData.py:150` — `updateExtrasByKey` mutates an alias and returns nothing; clarify contract.
- `iexplot/pynData/pynData_ARPES.py:229` — `_stack_Escale` derives `E_delta` from the last EA, assuming uniform spacing across all EAs; document or guard.
- `iexplot/fitting.py:344` — `find_EF_offset` docstring says "finds and applies" but only returns centers.
- `iexplot/plotting.py:514` / `pynData_plot.py:56` — stale docstrings (return dict commented out; "only 1d and 2d" but handles 3D).
- `iexplot/IEX_pkg/export_CASA_XPS.py:9` — writes `.vms` (VAMAS) extension but content is plain CSV; CASA won't parse as VAMAS.
- `iexplot/IEX_pkg/IEX_nData.py:428` — `info()` never reports MCA loads.
- `iexplot/IEX_pkg/IEX_MCA.py:40` — `IEX_MCA` overrides `__init__`/`_update_attr` and drops the parent's `suffix` attribute.
- `iexplot/spec_write/Octuople_spec_file.py` — filename misspelled ("Octuople" vs "Octupole"); function names mix both spellings.
- `iexplot/mda/__init__.py` — `from .mda import *` with no `__all__` leaks `add/sub/mul/div/main/string/copy` into the namespace; builtins shadowed as locals (`dict`, `all`, `map`) in `readMDA`/`showEnv`.
- `iexplot/mda_quick_plot.py:343` — `plot_mda_series` uses `exec(cmd)`; call `plot_mda` directly.
- Consolidate the two fitting stacks (`iexplot/fitting.py` curve_fit vs `pynData/{fit1D,fit2D}.py` lmfit) or document when to use which.
- Consider splitting the 3.3k-line `mda/mda.py` (read / write / ascii / arithmetic / CLI) and de-vendoring `mdaUtils.py`.

---

## Suggested priority order

1. **spec_write** — fix or quarantine; it cannot import today (start with `Kappa_spec_file.py:24`).
2. **High-severity live-path bugs** — `Plot_EA.make_EA_list:410` (avg), `IEX_nData:163/170` (AD key), `_sum_EAs:57` (list), `plotting.py:119`, `constants_conversions` (both), `pynData_fitting 'step:'`, `plot_nd_avg`.
3. **Repair or clearly mark broken APIs** — `nData.save()`, `nAppend()`, k-mapping functions, `mda_quick_plot` EA/nc paths.
4. **Kill duplication** — delete/re-export `mdaUtils.py`; unify ROI helpers; merge spec_write Kappa/Octuople.
5. **Systemic** — replace bare excepts; add an import smoke test + linter in CI.
