import os
import shutil
import sys

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from prfpylot.download_example import ExampleDownloadHandler
from prfpylot.constants import PROJECT_DIR, EXAMPLE_DIR


def prepare_pylot_test_environment(outdir_label: str) -> str:
    # download example data if not already present
    ExampleDownloadHandler.check_and_download_example_data(
        skip_confirmation=os.environ.get("NONINTERACTIVE", "0") == "1"
    )
    ExampleDownloadHandler.download_and_install_proffast()

    # possibly remove existing analysis
    analysis_dirpath = os.path.join(
        EXAMPLE_DIR,
        "data",
        "analysis",
        outdir_label[:-14],
    )
    if os.path.exists(analysis_dirpath):
        print(f"Analysis data already exists. Removing it to ensure a clean run.")
        shutil.rmtree(analysis_dirpath)

    # possibly remove existing results
    results_dirpath = os.path.join(
        EXAMPLE_DIR,
        "data",
        "results",
        outdir_label,
    )
    if os.path.exists(results_dirpath):
        print(f"Example data already exists. Removing it to ensure a clean run.")
        shutil.rmtree(results_dirpath)

    # possibly remove intermediate proffast results
    prf_wrk_dirpath = os.path.join(PROJECT_DIR, "prf", "wrk_fast")
    site_name = outdir_label.split("_")[0]
    print(
        f"Removing intermediate PROFFAST results in prf/wrk_fast that start with {site_name} to ensure a clean run."
    )
    for f in os.listdir(prf_wrk_dirpath):
        if f.startswith(site_name):
            os.remove(os.path.join(prf_wrk_dirpath, f))

    # return the expected results filepath to check later
    return os.path.join(
        results_dirpath,
        f"comb_invparms_{outdir_label}.csv",
    )
