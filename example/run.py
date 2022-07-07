"""
This is the example run script for the Sodankyla example data using the
PROFFASTpylot.
To execute this file you have to change your working directory to be
.../proffastpylot/example
"""

# It is important to use this if clause in windows to let the multiprocessing
# work properly.
if __name__ == "__main__":
    # Check if example input data is already available on disk,
    # if not download it.
    # This is not needed for your personal PROFASTpylot run-file
    from prfpylot.download_example import ExampleDownloadHandler
    ExampleDownloadHandler().check_and_download_example_data()

    # The following part can be adapted to your own retrieval
    from prfpylot.pylot import Pylot

    input_file = "input_sodankyla_example.yml"
    MyPylot = Pylot(input_file, logginglevel="info")

    MyPylot.run(n_processes=2)
