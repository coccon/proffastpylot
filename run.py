# TODO: optional input parameters: list of dates or start and end-date
# python run.py --start xxx --stop xxx --input input.yml --sitename Sodankyla

from prfpylot.pylot import Pylot
from datetime import datetime as dt

MyPRFpylot = Pylot("input.yml")
#MyPRFpylot.run_preprocess(NumberOfProcesses=2)
# MyPRFpylot.generate_prf_input("inv", dt.now())
