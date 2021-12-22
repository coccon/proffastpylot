from prfpylot.pylot import Pylot
from prfpylot.create_inputfile import InputfileGenerator

if __name__ == "__main__":
    # if __name__ == "__main__" is necessary for multiprocessing
    try:
        # Generate Inputfile using the inputfile generator
        MyInpFileGen = InputfileGenerator()
        input_file = MyInpFileGen.generate_sod_example()
        
        MyPRFpylot = Pylot(input_file, logginglevel="debug")
        # MyPRFpylot.run(n_processes=2)
        MyPRFpylot.run_preprocess(n_processes=2)
        MyPRFpylot.run_pcxs(n_processes=2)
        MyPRFpylot.run_inv(n_processes=2)
        MyPRFpylot.combine_results()
    finally:
        MyPRFpylot.clean_files()
        
