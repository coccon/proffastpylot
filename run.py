# TODO: optional input parameters: list of dates or start and end-date
# python run.py --start xxx --stop xxx --input input.yml --sitename Sodankyla

from prfpylot.pylot import Pylot
import os


input_file = os.path.join(".", "input_sodankyla_example.yml")
MyPRFpylot = Pylot(input_file)
MyPRFpylot.run_preprocess(NumberOfProcesses=2)

# MyPRFpylot.run_preprocess(NumberOfProcesses=1)
# date = dt.strptime("170608", "%y%m%d")
# MyPRFpylot.generate_prf_input("pcxs", date)
