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
A folder `PROFFASTpylot` containing all program files will be created.

### Clone the prfpylot repository using git

Alternatively download and unpack the zip file 
https://git.scc.kit.edu/cw4643/prfpylot/-/archive/master/prfpylot-master.zip
Extracting it will create the folder `PROFFASTpylot`.



## 3. Get PROFFAST and copy to prfPylot

### Download PROFFAST
Download and install an up-to-date version of PROFFAST.

Clone the PROFFAST Repository.
```
git clone https://git.scc.kit.edu/imk-asf-bod/proffast.git
```

Alternatively you can also download and unpack the zip file 
https://git.scc.kit.edu/imk-asf-bod/proffast/-/archive/main/proffast-main.zip

**For Linux users**: Run the installation script to create the executables.  
```
./install_proffast_linux.sh
```
For Windows users, the executables are already provided.

### Copy PROFFAST directory into prfPylot

Copy the PROFFAST directory into `PROFFASTpylot` and rename it to `prf`.

**For Linux Users**: Instead copying the directory you can create a symlink with e.g.
```
cd PROFFASTpylot
ln -s ../proffast prf
```



## 3. Create a virtual environment in python

We recommend using a virtual environment (venv) to avoid conflicts between any other packages or Python modules.

2. Navigate to the `PROFFASTpylot` folder using a terminal.
3. Enter `python -m venv prf_venv`
   This command will create a folder named `prf_venv` which contains the virtual environment
4. Activate the virtual environment with
   - *Windows PowerShell:* `.\prf_venv\Scripts\Activate.ps1`  
   - *Windows Commandline:* `.\prf_venv\Scripts\activate` 
   - *Linux:* `source ./prf_venv/bin/activate`
5. To deactivate run `deactivate`

Note that all packages to be installed with `pip install` will only affect the virtual environment and not the local Python installation.  
Note that bevore each run of prfpylot you need to activate the virtual environment by executing the command from step 4.

In case of a problem, take a look at the [Troubleshooting](https://git.scc.kit.edu/cw4643/prfpylot/-/blob/master/docs/troubleshooting.md) page.





## 4. Install the prfPylot repository

Activate the virtual environment (see above).

Navigate to `PROFFASTpylot` and enter
```
pip install --editable .
```





## 5. Resulting folder structure

If you follow the exactly the installation guide your folder strucutre should look like the following:
```
PROFFASTpylot
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