# TODO: optional input parameters: list of dates or start and end-date
# python run.py --start xxx --stop xxx --input input.yml --sitename Sodankyla

from prfpylot.prfpylot import Pylot

MyPRFpylot = Pylot()
MyPRFpylot.generate_prf_input("prep")
