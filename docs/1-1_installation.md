# Installation


## Content

1. Prerequisites
2. Download the PROFFASTpylot repository
3. Get PROFFAST and copy it to `proffastpylot`
4. Create a virtual environment in Python
5. Install PROFFASTpylot
6. Resulting folder structure
7. Test the installation by running an example dataset
8. Getting Updates

## 1. Prerequisites

To use PROFFASTpylot, you need Python 3.7 or newer. The PROFFAST and PROFFASTpylot can be used in Windows and Linux environments. A step-by-step installation instruction for both environments is provided below. We did not test the software for Mac environments. 

## 2. Download the PROFFASTpylot repository

### Clone the PROFFASTpylot repository using git

**We recommend downloading the files using git (https://www.git-scm.com).**  
 
It will make future updates easier.

```bash
git clone https://gitlab.eudat.eu/coccon-kit/proffastpylot.git
```

A folder `proffastpylot` containing all program files will be created.

### Alternatively: Download the PROFFASTpylot repository as a zip file

If you do not want to use git, you can instead download and unpack the zip file https://gitlab.eudat.eu/coccon-kit/proffastpylot/-/archive/master/proffastpylot-master.zip

Extracting it will create the folder `proffastpylot`.

## 3. Get PROFFAST and copy it to the proffastpylot folder

### Download PROFFAST

Download PROFFAST Version 2.4 from the KIT website: https://www.coccon.kit.edu/69.php

### Compile PROFFAST (only Linux)

For Windows users, the executables are already provided; on Linux systems, you need to create them from source. If not present on your system, first install the `gfortan` compiler. Secondly, run the installation script for compilation from the `prf` folder.

```bash
cd prf/
bash install_proffast_linux.sh
```

### Copy the prf directory

Copy the `prf` folder that was extracted from the zip file into `proffastpylot`.

## 4. Create a virtual environment in Python

We recommend using a virtual environment (venv) to avoid conflicts between any other packages or Python modules.

1. (Only first time) Navigate to the `proffastpylot` folder using a terminal.
2. (Only first time) Enter `python -m venv .venv`. This command will create a folder named `.venv`, which contains the virtual environment
3. **Activate the virtual environment** every time you run PROFFASTpylot with
   - *Windows PowerShell:* `.\.venv\Scripts\Activate.ps1`
   - *Windows Commandline:* `.\.venv\Scripts\activate`
   - *Linux:* `source .venv/bin/activate`
4. To deactivate the virtual environment, you can run `deactivate`

Note that all packages installed with `pip install .` will only affect the virtual environment, not the system-wide  Python installation. In case of a problem, take a look at the **Troubleshooting** article of this documentation.

You need to activate the virtual environment before each run of PROFFASTpylot by executing the command in step 3; the other steps need to be executed only once in the initial installation.

## 5. Install the PROFFASTpylot repository

First, activate the virtual environment (see above). Navigate to `proffastpylot` and enter:

```bash
pip install --editable .
```

## 6. Resulting folder structure

If you follow exactly the installation guide, your folder structure should look like the following:

```
proffastpylot
├── .venv
│   ├── ...
├── docs
│   ├── ...
├── example
│   ├── input_sodankyla_example.yml
│   ├── log_type_pressure.yml
│   └── run.py
├── prf
│   ├── docs
│   ├── inp_fast
│   ├── inp_fwd
│   ├── preprocess
│   ├── source
│   ├── out_fast
│   └── wrk_fast
├── prfpylot
│   ├── ...
└── pyproject.toml
```

## 7. Test the installation by running an example dataset

To test the installation, we provide example raw data and a reference result file for comparison. The example can be executed by navigating to the example folder and executing `python run.py` (please ensure that your virtual environment is activated). When first running the program, it will ask you to download the example file data to your local computer.

After the run is complete, please compare your results to the data given in `example\Reference_Output_Example_Sodankyla.csv`. The deviations should be less than 0.1 ppm for XCO2, 0.1 ppb for XCH4, and 0.1 ppb for XCO.

## 8. Getting Updates

If you used git during installation, you can easily get updates by entering

```bash
git pull
```

in a `git bash` or in a Terminal in your `proffastpylot` folder. This command will download all available updates. If you downloaded PROFFASTpylot as a zip file, you need to redo all steps of this installation script.
