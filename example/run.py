from prfpylot.create_inputfile import InputfileGenerator
from prfpylot.pylot import Pylot

if __name__ == "__main__":

    # create the input file for the example data
    MyInputfileGenerator = InputfileGenerator()
    MyInputfileGenerator.generate_sod_example()
        
    # run proffast using the prfPylot
    input_file = "input_sodankyla_example.yml"
    MyPylot = Pylot(input_file, logginglevel="debug")
    MyPylot.run(n_processes=2)
