from prfpylot.create_inputfile import InputfileGenerator
from prfpylot.download_example import ExampleDownloadHandler
from prfpylot.pylot import Pylot

if __name__ == "__main__":

    # check if data is already available on disk. If not download it
    MyDownloader = ExampleDownloadHandler()
    MyDownloader.check_and_download_example_data()

    # create the input file for the example data
    MyInputfileGenerator = InputfileGenerator()
    input_file = MyInputfileGenerator.generate_sod_example()
    pressure_type = MyInputfileGenerator.get_log_type_pressure_path()

    # create prfPylot and run PROFFAST using the prfPylot
    MyPylot = Pylot(input_file, pressure_type, logginglevel="info")
    MyPylot.run(n_processes=2)
