# Check if example input data is already available on disk, if not download it.
# This is not needed for your personal PROFASTpylot steering file
from prfpylot.download_example import ExampleDownloadHandler
ExampleDownloadHandler().check_and_download_example_data()


# The following part can be adapted to your own retrieval
from prfpylot.pylot import Pylot

input_file = "input_sodankyla_example.yml"
MyPylot = Pylot(input_file, logginglevel="info")

if __name__ == "__main__":
    MyPylot.run(n_processes=2)
