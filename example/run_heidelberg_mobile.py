from prfpylot.pylot import Pylot

proffastpylot_parameters = {
    "instrument_number": "SN119",
    "site_name": "Heidelberg",
    "site_abbrev": "he",
    "coord_file": "input_data/coords.csv",
    "interferogram_path": "input_data/interferograms/SN119",
    "map_path": "input_data/pressure_coords_mobile",
    "pressure_path": "input_data/pressure_coords_mobile",
    "pressure_type_file": "vaisala_pressure_parameters.yml",
    "coord_type_file": "mira_coord_parameters.yml",
    "analysis_path": "analysis",
    "result_path": "results",
    "coord_path": "input_data/pressure_coords_mobile",
    "altitude_factor": 1e-3,  # conversion to km
}

Pylot(proffastpylot_parameters).run()
