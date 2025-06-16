from prfpylot.pylot import Pylot

input_file = "proffastpylot_parameters_tsukuba.yml"
if __name__ == "__main__":
    Pylot(input_file).run(n_processes=2)
