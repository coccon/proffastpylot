
## commit 2026-11-14

More CPython bugs we need to work around when trying to kill a parent process
with several sub-processes

  Both forms, not just one (2026-11-13) - os.killpg(p.pid, ...) only finds
  anything if this worker's own os.setpgrp() (_pool_worker_init(), above) has
  already run by the time we get here. Pool()'s constructor only guarantees the
  fork happened, not that the child has finished executing its initializer - a
  worker interrupted in that window is still a member of the *original* shared
  process group, so killpg(p.pid, ...) (pgid == p.pid only after setpgrp()
  succeeded) finds no matching group, raises ProcessLookupError, and silently
  no-ops - leaving that one worker alive and orphaned. Confirmed for real: a live
  Ctrl+C test left exactly this behind - the main process returned to the shell
  correctly (so this bug was invisible from there), but 10 worker processes sat
  orphaned, re-parented and unreaped, for hours afterward. os.kill(p.pid, ...)
  unconditionally kills the worker PID itself regardless of which group it's
  still in, closing that race; os.killpg(...) is kept alongside it for the normal
  case (setpgrp() already ran) since it additionally takes out whatever Fortran
  subprocess that worker is still running, which a plain os.kill() of the worker
  alone would leave orphaned on its own.

## commit 2026-11-13


  Fix Ctrl+C hang in multiprocessing.Pool steps; path overrides and packaging fixes

- pylot.py: structural fix for a long-standing CPython bug (bpo-8296/9205, never fixed for
    multiprocessing.Pool) where a worker interrupted by Ctrl+C can die without reporting a
    result, hanging Pool.terminate()'s internal thread-join forever. Added
    _pool_worker_init()/_run_pool_map(): workers are isolated into their own process group via
    os.setpgrp() so they never see SIGINT directly; on any exception from pool.map(), the main
    process hard-kills each worker's whole group (taking its external Fortran binary with it)
    and cancels the Pool's own atexit Finalize instead of letting it hang. Replaces the
    2026-11-11 point fix in _call_external_program() (kept as a harmless defensive second
    layer), which only covered one of several interrupt-landing-points.

- prepare.py: let a caller (gbp_lib3) override analysis_instrument_path/result_folder
    explicitly instead of always deriving them from site_name/instrument_number.

- pyproject.toml: pin numpy==2.4.6 (was >=2.4.6); stop excluding prfpylot* from the package
    build, since gbp_lib3 needs it importable.

Info on changes in PRF FORTRAN code:
- preprocess62/pcxs24/invers26 (under `prf/`, entirely gitignored in this
  repo per `.gitignore`'s `prf/*` - nothing below shows up in `git status`
  or any commit here) gained a `--version` CLI flag each, and preprocess62
  gained 8 new per-measurement diagnostics (MNY, MXY, SNR, ZPA,
  zpa_fb_rdiff, DIP, wn_shift, fwd_bwd_res_diff) written as new trailing
  columns on `cal/logfile.dat`, mostly ported from or inspired by GGG2020.1's
  i2s preprocessor. Full writeup, including two real bugs found and fixed
  during testing, is in `prf/docs/change_log.md` - kept separate since none
  of it is git-tracked here. These are local, uncommitted edits pending
  review/testing and a possible upstream submission to the PROFFAST
  maintainer - not part of this repo's own history.

## commit 2026-09-07

- Created a new branch "proffastpylot_gbp" for using PROFFASTpylot with the CO2M mission ground-based processor GBP.

- Relax numpy pin from ==2.4.1 to >=2.4.6 in the toml file

All other dependencies here are exact-pinned as a lockfile-style
snapshot rather than genuine minimum-version constraints. numpy==2.4.1
specifically conflicted with numpy>=2.4.6 already required by
write_tccon_netcdf in the shared gbp3 environment -- a plain
pip install would silently downgrade numpy and break that
requirement. Checked the numpy call sites actually used here
(np.array, np.zeros, np.interp, np.float32/64, np.datetime64,
np.bytes_, np.amax/amin, np.savetxt, np.longdouble) -- all long-stable
mainstream APIs, unaffected by anything between 2.4.1 and 2.4.6 (same
2.4 minor line, no API changes between patch releases per numpy's own
compatibility policy).

