# Installation

_For using prfPylot you need Python 3.7 or newer._

## Content

1. Download the prfPylot repository
2. Get PROFFAST and copy to prfPylot
3. Create a virtual environment in python
4. Install the prfPylot repository
5. Resulting folder_structure



## 1. Download the prfPylot repository

**We recommend downloading the files using [git](https://www.git-scm.com).**   
It will make future updates easier.


### Clone the prfpylot repository using git

```   
git clone git@git.scc.kit.edu:cw4643/prfpylot.git
```
A folder `proffastpylot` containing all program files will be created.


### Clone the PROFFASTpylot repository using git

Alternatively download and unpack the zip file 
https://gitlab.eudat.eu/coccon-kit/proffastpylot/-/archive/master/proffastpylot-master.zip
Extracting it will create the folder `proffastpylot`.



## 3. Get PROFFAST and copy it to the program folder

### Download PROFFAST
Download and install an up-to-date version of PROFFAST.
It can be found on the KIT website:  
https://www.imk-asf.kit.edu/english/3225.php

**For Linux users**: Run the installation script to create the executables. 
```
./install_proffast_linux.sh
```
For Windows users, the executables are already provided.


### Copy the PROFFAST directory into proffastpylot

Copy the PROFFAST directory into `proffastpylot` and rename it to `prf`.

**For Linux Users**: Instead copying the directory you can create a symlink with e.g.
```
cd proffastpylot
ln -s ../proffast prf
```



## 3. Create a virtual environment in python

We recommend using a virtual environment (venv) to avoid conflicts between any other packages or Python modules.

2. Navigate to the `proffastpylot` folder using a terminal.
3. Enter `python -m venv prf_venv`
   This command will create a folder named `prf_venv` which contains the virtual environment
4. Activate the virtual environment with
   - *Windows PowerShell:* `.\prf_venv\Scripts\Activate.ps1`  
   - *Windows Commandline:* `.\prf_venv\Scripts\activate` 
   - *Linux:* `source ./prf_venv/bin/activate`
5. To deactivate run `deactivate`

Note that all packages to be installed with `pip install` will only affect the virtual environment and not the local Python installation.  
In case of a problem, take a look at the [Troubleshooting](https://git.scc.kit.edu/cw4643/prfpylot/-/blob/master/docs/troubleshooting.md) page.

You need to activate the virtual environment bevore each run of the PROFFASTpylot by executing the command from step 4.



## 4. Install the PROFFASTpylot repository

Activate the virtual environment (see above).

Navigate to `proffastpylot` and enter
```
pip install --editable .
```


## 5. Resulting folder structure

If you follow the exactly the installation guide your folder strucutre should look like the following:
```
proffastpylot
├── prf_venv
│   ├── ...
├── docs
│   ├── ...
├── example
│   ├── input_data
│   ├── input_sodankyla_example.yml
│   └── run.py
├── prf
│   ├── docs
│   ├── inp_fast
│   ├── inp_fwd
│   ├── preprocess
│   ├── source
│   └── wrk_fast
├── prfpylot
│   ├── ...
└── setup.py
```