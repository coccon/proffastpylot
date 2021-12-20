# TODO: optional input parameters: list of dates or start and end-date
# python run.py --start xxx --stop xxx --input input.yml --sitename Sodankyla

from prfpylot.pylot import Pylot
import os
import time

if __name__ == "__main__":
    # if __name__ == "__main__" is necessary for multiprocessing
    try:
        input_file = "input_sodankyla_example.yml"
        MyPRFpylot = Pylot(input_file, logginglevel="info")
        # MyPRFpylot.run(n_processes=2)
        
        #MyPRFpylot.run_preprocess(n_processes=2)
        #MyPRFpylot.run_pcxs(n_processes=2)
        MyPRFpylot.run_inv(n_processes=2)
        MyPRFpylot.combine_results()
    finally:
        MyPRFpylot.clean_files()
        
