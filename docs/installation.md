# Installation

## Content

1. Get PROFFAST
2. Clone and install the prfPylot repository
3. Copy the PROFAST directory into prfPylot

## Get PROFFAST

First, download and install an up-to-date version of PROFFAST.

Clone the PROFFAST Repository.   
`git clone https://git.scc.kit.edu/imk-asf-bod/proffast.git`

**For Linux Users**: Run the script installation script to create the executables.  
`./install_proffast_linux.sh`  
For Windows users, the executables are already provided.


## Clone and install the prfPylot repository

Clone the prfpylot repository  
`git clone git@git.scc.kit.edu:cw4643/prfpylot.git`

Install it via pip:  
`pip install --user --editable .`  
prfPylot is written with python3. We recommend using python >= 3.7.


## Copy PROFFAST directory into prfPylot

Copy the PROFFAST directory into `prfpylot` and rename it to `prf`.

**For Linux Users**: Instead copying the directory you can create a symlink with e.g.
```
cd prfpylot
ln -s ../proffast prf
```
