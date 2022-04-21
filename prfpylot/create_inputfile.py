"""create_inputfile is a module of PROFFASTpylot.

The InputfileGenerator class can produce input files in an interactive mode,
or matching the Sodankyla example data.

It can be executed as a standalone script.

Usage:
If started without additional arguments the
If started as `python create_inputfile.py --example-mode`
The inputfile for the Sodankyla example is created.


License information:
PROFFASTpylot - Running PROFFAST with Python
Copyright (C)   2022    Lena Feld, Benedikt Herkommer,
                        Karlsruhe Institut of Technology (KIT)

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License version 3 as published by
the Free Software Foundation.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""

import os
import sys
import datetime as dt


class InputfileGenerator():
    """Generation of input files.

    functions:
        generate_sod_example: create an input file for the provided
            example data of Sodankyla.
        interactive_inputfile_generation: fill in the required information
            in a command line dialogue.
    """
    def __init__(self):
        """Create an input file for the provided example data of Sodankyla.
        """

        # self.prfpylot_path = prfpylot.__path__[0]
        self.scriptpath = os.path.abspath(os.path.dirname(__file__))
        self.inptfl_template = os.path.join(self.scriptpath, "templates",
                                            "template_input.yml")
        # a dict where the config is safed:
        self.input_data = {}

    def generate_sod_example(self):
        """
        This methods contains the hardcoded path to the example files
        """
        # the path where the final inputfile is writte to
        # Old version, does not work if installed without --editable
        # self.inptfl_path = os.path.join(self.scriptpath, "..", "example")
        # New version, more robust
        self.inptfl_path = os.getcwd()
        self.inptfl = os.path.join(
                                self.inptfl_path,
                                "input_sodankyla_example.yml")
        inputpath = os.path.normpath(os.path.join(self.scriptpath, "..",
                                     "example", "input_data"))

        # the data which is used to fill the template
        self.input_data["instrument_number"] = "SN039"
        self.input_data["site_name"] = "Sodankyla"
        self.input_data["site_abbrev"] = "so"
        self.input_data["lat"] = ""
        self.input_data["lon"] = ""
        self.input_data["alt"] = ""
        self.input_data["coord_file"] = os.path.join(inputpath, "coords.csv")
        self.input_data["utc_offset"] = ""
        self.input_data["start_date"] = ""
        self.input_data["end_date"] = ""
        self.input_data["note"] = ""

        self.input_data["delete_abscosbin_files"] = "True"
        self.input_data["delete_input_files"] = "False"
        self.input_data["igram_size_filter"] = 3.7
        self.input_data["start_with_spectra"] = "False"
        self.input_data["pressure_type"] = os.path.join(
            inputpath, "..", "log_type_pressure.yml")
        self.input_data["tccon_mode"] = "False"
        self.input_data["tccon_setting"] = "0"

        igram_path = os.path.join(inputpath, "interferograms_sodankyla",
                                  "SN039")
        self.input_data["interferogram_path"] = os.path.normpath(igram_path)
        map_path = os.path.join(inputpath, "map_sodankyla")
        self.input_data["map_path"] = os.path.normpath(map_path)

        pressure_path = os.path.join(inputpath, "pressure_sodankyla")
        self.input_data["pressure_path"] = os.path.normpath(pressure_path)

        result_path = os.path.join(self.scriptpath, "..", "example",
                                   "results")
        self.input_data["result_path"] = os.path.normpath(result_path)

        analysis_path = os.path.join(self.scriptpath, "..", "example",
                                     "analysis")
        self.input_data["analysis_path"] = os.path.normpath(analysis_path)

        prf_path = os.path.join(self.scriptpath, "..", "prf")
        self.input_data["proffast_path"] = os.path.normpath(prf_path)

        self._generate_inputfile()
        return self.inptfl

    def get_log_type_pressure_path(self):
        pressurepath = os.path.normpath(
            os.path.join(
                self.scriptpath, "..", "example", "log_type_pressure.yml"))
        return pressurepath

    def interactive_inputfile_generation(self):
        """
        Generate the input file interactivly with a command line dialogue.
        """
        hashtg = "####################"
        spaces = "                    "
        print(
            f"#{hashtg}######################################{hashtg}#\n"
            f"#{spaces}  Welcome to the inputfile generator. {spaces}#\n"
            f"#{spaces}  This tool is part of PROFFASTpylot. {spaces}#\n"
            f"#{hashtg}######################################{hashtg}#\n"
        )
        print(
            "This tool helps you to create the inputfile of PROFFASTpylot to "
            "run the files of one device at one location.\n"
            "Please generate a unique inputfile (manually or by using this "
            "tool) for each instrument and each location. Please note, that "
            "files like pressure and *.map files can be shared among various "
            "intruments at the same site."
        )
        temp = input("To start the configuration press enter")
        print(
            "############ Data paths ############\n\n"
            "Please give the path to the PROFFAST executable.\n"
            "In this folder the PROFFAST executable have to be"
            " located.")
        defaultprf = os.path.abspath(
            os.path.join(self.scriptpath, "..", "prf"))
        print(
            "As the automatic detected default value the following path is "
            f"used:\n{defaultprf}\n"
            "To use this path do not enter anything and press enter:")
        temp = input()
        if temp == "":
            temp = defaultprf
        self.input_data["proffast_path"] = temp

        temp = input(
            "Please give the path to the interferograms. "
            "Within this folder the igrams have to be stored using "
            "the convention 'YYMMDD/YYMMDDSN.XXX':\n"
            "Example: If your data are saved like this\n"
            "D:\\RawDataEM27\n"
            "|__170608\n"
            "|  |_170608.001\n"
            "|  |_170608.002\n"
            "|  |_...\n"
            "|__YYMMDD\n"
            "|  |_YYMMDD.XXX\n"
            "you have to enter 'D:\\RawDataEM27'\n")
        self.input_data["interferogram_path"] = temp

        temp = input("\nPlease give the path of the map files:\n")
        self.input_data["map_path"] = temp

        temp = input("\nPlease give the path of the pressure files:\n")
        self.input_data["pressure_path"] = temp

        temp = input("\nPlease give the path of the analysis folder.\n"
                     "In a standard installation it located in the same folder"
                     " as the PROFFAST executables.\n"
                     "To use the default value press enter without any input."
                     "\nDefault: proffast_path/analysis\n")
        if temp == "":
            temp = os.path.join(self.input_data["proffast_path"], "analysis")
        self.input_data["analysis_path"] = temp

        temp = input(
            "\nPlease give the path where the results are to be saved:\n"
            )
        self.input_data["result_path"] = temp

        print("\n\n############ Site Specific Information ############\n")
        temp = input("Please give the name of your site (e.g. Sodankyla):\n")
        self.input_data["site_name"] = str(temp)

        temp = input("\nPlease give the instrument number (e.g. SN039):\n")
        self.input_data["instrument_number"] = str(temp)

        temp = input("\nPlease give the site abbreviation as given in the map"
                     "-files:\n")
        self.input_data["site_abbrev"] = temp

        temp = input("\nCoordinates:\n"
                     "Do you want to specify coordinates or do you want to"
                     " use the coordinates given in the coordinate file?\n"
                     "Please write either 'custom' or 'file':\n")
        while True:
            if temp == "custom" or temp == "file":
                break
            else:
                temp = input("Could not read input!\n"
                             "Please give either 'file'"
                             " for taking the coordinate from the file or "
                             "'custom' if you want to specify them in the"
                             " following:\n")
        if temp == "file":
            self.input_data["lat"] = ""
            self.input_data["lon"] = ""
            self.input_data["alt"] = ""
            temp = input("\nPlease give the path to the coord-file:\n")
            self.input_data["coord_file"] = temp
        elif temp == "custom":
            self.input_data["coord_file"] = ""
            print("NOTE: Please give the coordinates with an accuracy of"
                  " 5 digits!")
            abbrv = ["lat", "lon"]
            coord_text = ["latitude", "longitude"]
            for i, coord in enumerate(coord_text):
                temp = input(f"Please give the {coord}:\n")
                while True:
                    try:
                        temp = float(temp)
                        break
                    except ValueError:
                        temp = input("Could not read input. Please give a "
                                     "Number with 5 digits and a dot as  "
                                     "decimal sign:\n")
                self.input_data[abbrv[i]] = "{:07.5f}".format(temp)
            temp = input("\nPlease give the altitude in meter:\n")
            while True:
                try:
                    temp = float(temp)
                    break
                except ValueError:
                    temp = input("Could not parse input. Please give a "
                                 "Number:\n")
            self.input_data["alt"] = temp

        # TODO: Find out in which format the UTC-offset is needed.
        temp = input(
            "\nIf your igrams have a UTC-offset plase give it "
            "here. If not just leave it empty and press enter: \n")
        self.input_data["utc_offset"] = temp

        print(
            "\nIf you do not want to process all interferograms of your site\n"
            "you can now specify a start and stop date.\n"
            "Leave it empty if you want to process all dates:")
        strt_stp = ["start", "end"]
        for i, strtstp in enumerate(strt_stp):
            temp = input(f"Please give the {strtstp} date in YYYY-MM-DD:\n")
            if temp == "":
                self.input_data[f"{strtstp}_date"] = ""
            else:
                while True:
                    try:
                        temp = dt.date.fromisoformat(temp)
                        break
                    except ValueError:
                        temp = input(
                            "Could not parse input. Plase give as "
                            "YYYY-MM-DD:\n")
                self.input_data[f"{strtstp}_date"] = temp.isoformat()

        temp = input(
            "\nIf you want to add some notes to the spectra files please give"
            " it here. Limited to 80 characters:\n")
        while True:
            if len(temp) < 80:
                self.input_data["note"] = temp
                break
            else:
                temp = input("Note was to long. Give a shorter one:\n")

        print("\n############ Behaviour settings ############\n")
        temp = input(
            "File size filter for interferograms:"
            " All interferograms with a size less than the value entered here "
            "are assumed to be corrupted and are NOT used in the processing "
            "chain.\nThe default value is: 3.7355880737304688 MB\n"
            "Enter a filesize in MegaBytes:"
        )
        while True:
            if temp == "":
                self.input_data["igram_size_filter"] = 3.7355880737304688
                break
            try:
                temp = float(temp)
                break
            except (ValueError):
                temp = input("Could not parse the input."
                             "Please enter a floating point number:\n"
                             )

        temp = input(
            "Process already available spectra:\n"
            "If the spectra of a measurement are already available this has "
            "to be given here. This can happen if e.g. you want to reprocess "
            "some data with other pressure values or a-priori files.\n"
            "Only process spectra? Yes/No\n"
        )
        while True:
            if temp == "Yes":
                self.input_data["start_with_spectra"] = True
                break
            elif temp == "No":
                self.input_data["start_with_spectra"] = False
                break
            else:
                temp = input("Could not parse input. Enter 'Yes' or 'No'.:\n")

        temp = input(
            "Do you want to delete the abscos.bin files after the execution?\n"
            "These file contain the simulation of the atmosphere which is the "
            "result or the "
            "'pcxs' program. To keep the files can save computation time if "
            "you want to "
            "calculate some spectra of the same location in the same datetime "
            "range again. "
            "Delete absocs.bin file? Yes/No?\n"
        )
        while True:
            if temp == "Yes":
                self.input_data["delete_abscosbin_files"] = True
                break
            elif temp == "No":
                self.input_data["delete_abscosbin_files"] = False
                break
            else:
                temp = input("Could not parse input. Enter 'Yes' or 'No'.:\n")

        temp = input(
            "Do you want to delete the input files after the execution?\n"
            "If the inpuf files are not deleted they are moved after "
            "execution to the result "
            "folder specified earlier. It could be usefull to keep the input "
            "files for to "
            "find potential errors and to understand the evaluation after "
            "some time. "
            "Delete input files? Yes/No?\n"
        )
        while True:
            if temp == "Yes":
                self.input_data["delete_input_files"] = True
                break
            elif temp == "No":
                self.input_data["delete_input_files"] = False
                break
            else:
                temp = input("Could not parse input. Enter 'Yes' or 'No'.:\n")

        temp = input(
            "How to should PROFFASTpylot handle your pressure input? "
            "There is the possibility to create the 'pt_intraday.inp' "
            "directly. To choose this option enter 'original'. "
            "The other implemented option is to use the datalogger format as "
            "used in KA. For this type 'log'. "
            "Default is 'log':\n "
        )
        if temp == "":
            self.input_data["pressure_type"] = "log"
        else:
            self.input_data["pressure_type"] = temp

        temp = input(
            "Do you want to enable TCCON mode? "
            "This setting is only needed if you want to process "
            "interferograms which where recoreded with a TCCON-Spectrometer.\n"
            "Default: 'No'. Yes/No.\n"
        )
        while True:
            if temp == "Yes":
                self.input_data["tccon_mode"] = "True"
                break
            elif temp == "No":
                self.input_data["tccon_mode"] = "False"
                self.input_data["tccon_setting"] = 0
                break
            else:
                temp = input("Could not parse input. Enter 'Yes' or 'No'.\n")

        if self.input_data["tccon_mode"] == "True":
            temp = input(
                "What kind of TCCON setup do you use? Enter 1 or 2:\n"
                ": OPUS file containing one interferogram covering extended "
                "InGaAs. Spectral range (standard TCCON setup)\n"
                " 2: OPUS file containing two interferograms "
                "(CO band in separate filter band, KA setup)\n"
                "Enter '1/2':\n"
            )
            while True:
                if temp == "1" or temp == "2":
                    self.input_data["tccon_setting"] = temp
                    break
                else:
                    temp = input("Could not parse input. Enter '1' or '2' \n")

        print("\n############ Path of config file ############\n")
        temp = input("Please give the path (not the filename!) where the new "
                     "config-file (the output file of this tool) is supposed"
                     " to be stored:\n")
        self.inptfl_path = temp
        temp = input("\nPlease give the filename of the new config file. "
                     "If nothing is given the filename will be \n"
                     "'input_sitename_instrumentname.yml':\n")
        if temp == "":
            temp = f"{self.input_data['site_name']}_"\
                   + f"{self.input_data['instrument_number']}.yml"
            self.inptfl = os.path.join(self.inptfl_path, temp)
        elif ".yml" in temp:
            self.inptfl = os.path.join(self.inptfl_path, temp)
        else:
            temp += ".yml"
            self.inptfl = os.path.join(self.inptfl_path, temp)
        # Finally we have all information we need. Create the file:
        self._generate_inputfile()

    def _generate_inputfile(self):
        """
        Generate the inpufile by replacing the %xxx% sections with the
        corresponding value.
        """
        templ_stream = open(self.inptfl_template, 'r')
        config_stream = open(self.inptfl, 'w')
        for line in templ_stream:
            new_line = line
            for key, parameter in self.input_data.items():
                new_line = new_line.replace(
                    '%{}%'.format(key), str(parameter))
                new_line = self._replace_backslash(new_line)
            config_stream.write(new_line)
        templ_stream.close()
        config_stream.close()

    def _replace_backslash(self, line):
        """Replace backslash with slash if run on linux."""
        if sys.platform == "linux":
            return line.replace("\\", "/")
        return line


if __name__ == "__main__":
    import argparse

    MyGenerator = InputfileGenerator()
    parser = argparse.ArgumentParser()
    parser.add_argument("--example_mode",
                        help="Create the input file for the Sodankyla Example",
                        action="store_true")
    args = parser.parse_args()
    if args.example_mode:
        inputfile = MyGenerator.generate_sod_example()
        print(f"The inputfile was saved under {inputfile}")
    else:
        MyGenerator.interactive_inputfile_generation()
