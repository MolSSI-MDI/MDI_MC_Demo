MDI_MC_Demo
==============================
[//]: # (Badges)
[![GitHub Actions Build Status](https://github.com/REPLACE_WITH_OWNER_ACCOUNT/MDI_MC_Demo/workflows/CI/badge.svg)](https://github.com/REPLACE_WITH_OWNER_ACCOUNT/MDI_MC_Demo/actions?query=workflow%3ACI)
[![codecov](https://codecov.io/gh/REPLACE_WITH_OWNER_ACCOUNT/MDI_MC_Demo/branch/master/graph/badge.svg)](https://codecov.io/gh/REPLACE_WITH_OWNER_ACCOUNT/MDI_MC_Demo/branch/master)


A very basic Monte Carlo code intended to be used as part of an MDI engine tutorial.

# Overview

This code performs simple Monte Carlo simulations in which particles interact via a Lennard-Jones potential.
The purpose of this repository is to serve as the starting point for an MDI tutorial that demonstrates the process of implementing an MDI interface in an existing production code.  The full tutorial is provided later in this README file, in the Tutorial section.

# Tutorial

## Prerequisites

This tutorial will use [MDI Mechanic](https://github.com/MolSSI-MDI/MDI_Mechanic), which must be installed on your system:

```pip install mdimechanic```

MDI Mechanic uses Docker extensively, so you must also install Docker and launch Docker Desktop.
In order to more easily view the output from MDI Mechanic, it is recommended that you install an offline markdown viewer, such as `grip`:

```pip install grip```

## Using MDI Mechanic

Start an MDI Mechanic project:

```
mkdir MDI_MC_Demo_Report
cd MDI_MC_Demo_Report
mdimechanic startproject --enginereport
```

This will add several new files to the `MDI_MC_Demo_Report` directory, including one called `mdimechanic.yml`.



### Copyright

Copyright (c) 2021, Taylor Barnes


#### Acknowledgements
 
Project based on the 
[Computational Molecular Science Python Cookiecutter](https://github.com/molssi/cookiecutter-cms) version 1.5.
