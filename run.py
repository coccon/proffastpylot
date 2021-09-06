# TODO: optional input parameters: list of dates or start and end-date
# python run.py --start xxx --stop xxx --input input.yml --sitename Sodankyla

from prfpylot.pylot import Pylot
import os
from datetime import datetime as dt

if __name__ == "__main__":
    # if __name__ == "__main__" is necessary for multiprocessing
    input_file = os.path.join(".", "input_sodankyla_example.yml")
    MyPRFpylot = Pylot(input_file)
    # MyPRFpylot.run_preprocess(NumberOfProcesses=2)
    # MyPRFpylot.run_pcxs(NumberOfProcesses=2)
    MyPRFpylot.run_inv(NumberOfProcesses=2)
    #MyPRFpylot.move_result_files()
