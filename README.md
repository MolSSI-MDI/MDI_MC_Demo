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

MDI Mechanic uses Docker extensively, so **you must also install Docker Desktop and launch it**.
In order to more easily view the output from MDI Mechanic, it is recommended that you install an offline markdown viewer, such as `grip`:

```pip install grip```

## Start an MDI Mechanic project

Start an MDI Mechanic project with the following commands:

```
mkdir MDI_MC_Demo_Report
cd MDI_MC_Demo_Report
mdimechanic startproject --enginereport
```

This will add several new files to the `MDI_MC_Demo_Report` directory, including one called `mdimechanic.yml`.

## Configure the MDI Mechanic YAML file

The mdimechanic.yml file created in the previous step is used by MDI Mechanic to build your engine and to test and analyze its functionality as an MDI engine.
If you have used continuous integration (CI) testing services in the past, you will likely recognize many similarities between mdimechanic.yml and the YAML files that are often used by those services.
Open mdimechanic.yml in your favorite text editor, and you will see that MDI Mechanic pre-populated this file with a basic template.

This tutorial will go over each field in mdimechanic.yml in detail, but the following is a quick summary:

* **code_name:** The name of your code, which is used when printing out information.
* **image_name:** MDI Mechanic will create an Docker image, which will contain a highly portable environment that can be used to reproducibly build and run your engine. This field sets the name of the engine MDI Mechanic will create.
* **build_image:** This provides a script that is used to build the Docker image that MDI Mechanic builds. It corresponds to the steps required to prepare an environment with all of your engine's dependencies, and is comparable to a `before_install` step in some CI services.
* **build_engine:** This provides a script to build your engine. It is executed within the context of the Docker image built by MDI Mechanic, and is comparable to an `install` step in some CI services.
* **validate_engine:** This provides a script to verify that your engine has been built successfully. It is comparable to a `script` step in some CI services.
* **engine_tests:** This provides scripts used to test MDI functionality in your engine.

For now, just replace the value of `code_name` with the name of the engine (`MDI_MC_Demo`), and set the value of `image_name` to `mdi_mc_demo/mdi_report`

## Define the engine's dependencies using MDI Mechanic

This tutorial uses MDI Mechanic, which in turn runs your code within the context of a Docker image
In crude terms, you can think of an image as being a simulated duplicate of another computer, which has a different environment from yours (i.e. different installed libraries and system settings), and might be running an entirely different operating system.
The image created by MDI Mechanic is based on the Ubuntu Linux distribution.
Starting from the basic Linux environment, MDI Mechanic installs some basic compilers (`gcc`, `g++`, and `gfortran`), an MPI library (`MPICH`), Python 3, and a handful of other dependencies (`make` and `openssh`).
To finish building the image, MDI Mechanic executes whatever script you've provided in the `build_image` section of `mdimechanic.yml`.

We must now fill out `build_image` with an appropriate script that installs any dependencies necessary to run the `MDI_MC_Demo` engine.
If you look at `MDI_MC_Demo/MDI_MC_Demo.py`, you will see that in requires both `mpi4py` and `numpy`:

```
from mpi4py import MPI
import numpy as np
```

We want both of these dependencies to be installed during the `build_image` step.
In addition, we should install cmake and the MDI Library, as the engine will need it later.
Finally, we will want the image to have `git` installed, so that we can acquire a copy of the MDI_MC_Demo GitHub repository.
Modify the `build_image` step to read:
```
  build_image:
    - pip install mpi4py
    - pip install numpy
    - pip install cmake
    - pip install pymdi
    - apt-get update
    - apt-get install -y git
```

We can now check to see if MDI Mechanic is able to build the image by executing the following command, in the same directory where `mdimechanic.yml` is located:
```
mdimechanic build
```
This command may take a few minutes to execute, during which time Docker is working to build an image according to the instructions we gave it.
If everything worked correctly, you should see the following line printed out at the end:
```
Insert commands to build your engine code here
```
This line is printed by MDI Mechanic after it has built the image: specifically, after building the image, MDI Mechanic launches an instance of this image (*e.g.*, a container), and executes `build_engine` script in `mdimechanic.yml` **within that container**.
Our current `build_engine` script reads:
```
  build_engine:
    - echo "Insert commands to build your engine code here"
```
Unsurprisingly, when our new Docker container executes this script, it prints the line we saw at the end of the `mdimechanic build` execution.

## Build the engine using MDI Mechanic

We now need to modify the `build_engine` script so that it correctly acquires a clone of the MDI_MC_Demo Python package.
Because this engine is a Python script, it is not necessary to compile anything during the `build_image` step.
Modify the `build_engine` step to read:
```
  build_engine:
    - |
      if [ ! -d "build/MDI_MC_Demo" ]; then
        git clone https://github.com/MolSSI-MDI/MDI_MC_Demo.git build/MDI_MC_Demo
      fi
    - echo "Finished build_engine step"
```

Now if you execute `mdimechanic build` again, the output should end with:
```
Finished build_engine step
```

## Verify that the engine can be run

The primary purpose of MDI Mechanic is to portably validate MDI implementations.
You can run the full set of MDI Mechanic tests by executing the following command in the same directory where `mdimechanic.yml` is located:
```
mdimechanic report
```
The command will immediately return with the following error:
```
Exception: Error: Unable to verify that the engine was built.
```
The first test that MDI Mechanic performs is a test to confirm that the engine can be run successfully.
It does this by executing the script you provide in `validate_engine` in `mdimechanic.yml`.
We need to modify this script so that it corresponds to a basic test that confirms we are able to run the engine through MDI Mechanic.
The script should not test any MDI-specific functionality - it should only confirm that we can run MDI_MC_Demo.

Modify the `validate_engine` script so that it reads:
```
  validate_engine:
    - cd build/MDI_MC_Demo/MDI_MC_Demo
    - python MDI_MC_Demo.py
```
Now execute `mdimechanic report` again.
The output should indicate that MDI Mechanic was able to execute the `validate_engine` step successfully, but that it also found that MDI_MC_Demo lacks minimal MDI functionality:
```
Starting a report
Success: Able to verify that the engine was built
...
Exception: Error: Engine failed minimal MDI functionality test.
```
This is expected, since we have not yet begun to implement MDI support in MDI_MC_Demo.



## Implement basic MDI support

We will now begin to implement support for MDI_MC_Demo to act as an MDI engine.
When MDI Mechanic previously executed the `build_engine` step, it cloned the MDI_MC_Demo repository into `build/MDI_MC_Demo`.
Open the repository's Python code, which is located at `build/MDI_MC_Demo/MDI_MC_Demo/MDI_MC_Demo.py`.

We need to add `import mdi` to the file's import statements.
Later on, we will also need access to `sys`, so the full set of import statements should be:
```Python
from mpi4py import MPI
import numpy as np
import mdi
import sys
```

MDI engines are expected to accept `-mdi` command-line option, which allows the end-user to configure various MDI runtime options (*i.e.*, whether MDI will communicate between codes using MPI or TCP/IP sockets, *etc.*).
Modify the beginning of the `MCSimulation` initialization function to receive the `-mdi` command-line option:
```Python
class MCSimulation:
    def __init__(self):

        # Receive the -mdi option
        mdi_options = None
        self.use_mdi = False
        for iarg in range( len(sys.argv) ):
            if sys.argv[iarg] == "-mdi" or sys.argv[iarg] == "--mdi":
                if len(sys.argv) > iarg + 1:
                    mdi_options = sys.argv[iarg+1]
                    self.use_mdi = True
                else:
                    raise Exception('Argument to -mdi option was not provided')
```

Immediately after these lines, initialize the MDI Library:
```Python
        if self.use_mdi:
            mdi.MDI_Init(mdi_options)
```

Under the comment that reads `MPI Initialization` is the following line:
```Python
    self.world_comm = MPI.COMM_WORLD
```
Replace this line with:
```Python
        self.world_comm = MPI.COMM_WORLD
        if self.use_mdi:
            self.world_comm = mdi.MDI_MPI_get_world_comm()
```
This ensures that the MDI_MC_Demo engine will use the correct MPI communicator if the MDI communication is handled via MPI.

It is now necessary for the engine to establish a connection with the external driver.
At the end of the `MCSimulation` initialization function, add the following code:
```Python        
        self.mdi_comm = None
        if self.use_mdi:
            # Establish a connection with an external driver
            self.mdi_comm = mdi.MDI_Accept_communicator()

            # Set the MDI exit flag
            self.mdi_exit_flag = False
```

We now need to write code that will enable MDI_MC_Demo to receive and correctly respond to commands from the driver.
Add the following function to the `MCSimulation` class:
```Python
    def mdi_node(self, node_name, coordinates=None, energy=None):

        # Main MDI loop
        while not self.mdi_exit_flag:
            # Receive a command from the driver
            self.command = mdi.MDI_Recv_command(self.mdi_comm)

            # Broadcast the command to all ranks
            self.command = self.world_comm.bcast(self.command, root=0)

            # Respond to the received command
            if self.command == "EXIT":
                self.mdi_exit_flag = True
            else:
                # The received command is not recognized by this engine, so exit
                raise Exception('MDI Engine received unrecognized command: ' + str(self.command))
```

Finally, we will call this code immediately before the Monte Carlo simulation begins.
At the very beginning of the `MCSimulation` `run` function, insert a call to the `mdi_node` function:
This should look like:
```Python
        if self.use_mdi:
            self.mdi_node("@DEFAULT", coordinates=self.coordinates)
            if self.command == "EXIT":
                return
```

That's everything we need for basic MDI functionality.
Before MDI Mechanic can test our MDI implementation, we need to tell MDI Mechanic how to run MDI_MC_Demo as an MDI engine.
For a normal user, this is done simply by launching MDI_MC_Demo with an additional `-mdi` command-line option.
For example:
```
python MDI_MC_Demo.py -mdi "-name engine -role ENGINE -method TCP -hostname localhost -port 8021"
```
MDI Mechanic sets the argument to the `-mdi` option to an environment variable called `MDI_OPTIONS`.
Provide MDI Mechanic with an MDI-enabled launch script by modifying the contents of the `engine_tests` field in `mdimechanic.yml` to the following:
```
  node_search_distance: 1

  tested_commands:
    - '<CELL'
    - '<CELL_DISPL'
    - '<COORDS'
    - '<ENERGY'
    - '>ENERGY'
    - '<NAME'
    - '<NATOMS'
    - '@INIT_MC'
    - '@'
    - '<@'

  # Provide at least one example input that can be used to test your code's MDI functionality
  script:
    - cd build/MDI_MC_Demo/MDI_MC_Demo
    - python MDI_MC_Demo.py -mdi "${MDI_OPTIONS}"
```

Now execute `mdimechanic report` in the directory where `mdimechanic.yml` is located.
The first few lines of output should be:
```
Starting a report
Success: Able to verify that the engine was built
Success: Engine passed minimal MDI functionality test.
Success: Engine errors out upon receiving an unsupported command.
```

You may examine the completed report, which is located in a new `README.md` file, using `grip`.
If you execute `grip` in the directory where `mdimechanic.yml` and the new `README.md` file are located, you should see output similar to the following:
```
 * Serving Flask app "grip.app" (lazy loading)
 * Environment: production
   WARNING: This is a development server. Do not use it in a production deployment.
   Use a production WSGI server instead.
 * Debug mode: off
 * Running on http://localhost:6419/ (Press CTRL+C to quit)
```
Open the development server (located at `http://localhost:6419/` in the above example) in a web browser, and you will be able to see the report.

## Add support for the `<NATOMS`, `<COORDS`, `<CELL`, and `<CELL_DISPL` commands

We will now edit the `mdi_node` function to add support for the `<NATOMS` MDI command.
This command requires that the engine send the total number of atoms in its system to the driver.
We will need to add functionality for `MDI_MC_Demo` to do this as part of the `if ... else` clause that is labeled with the comment `Respond to the received command`
Add the following lines after the `command == "EXIT"` case:
```Python
            elif self.command == "<NATOMS":
                mdi.MDI_Send(self.num_particles, 1, mdi.MDI_INT, self.mdi_comm)
```
The full `if ... else` clause should look like:
```Python
            # Respond to the received command
            if self.command == "EXIT":
                self.mdi_exit_flag = True
            elif self.command == "<NATOMS":
                mdi.MDI_Send(self.num_particles, 1, mdi.MDI_INT, self.mdi_comm)
            else:
                # The received command is not recognized by this engine, so exit
                raise Exception('MDI Engine received unrecognized command: ' + str(self.command))
```

Supporting the `<COORDS` command follows a similar process, except that we must also convert `MDI_MC_Demo`'s internal coordinates from Lennard-Jones reduced units to atomic units, which are used by MDI.
The following code will accomplish this:
```Python
            elif self.command == "<COORDS":
                if coordinates is None:
                    raise Exception('The <COORDS command was received, but the coordinates are not available')
                conversion_factor = self.sigma * mdi.MDI_Conversion_factor("meter","atomic_unit_of_length")
                mdi_coords = conversion_factor * coordinates
                mdi.MDI_Send(mdi_coords, 3 * self.num_particles, mdi.MDI_DOUBLE, self.mdi_comm)
```

For the `<CELL` command, the engine must send its full set of cell vectors to the driver.
```Python
            elif self.command == "<CELL":
                conversion_factor = self.sigma * mdi.MDI_Conversion_factor("meter","atomic_unit_of_length")
                mdi_box_length = conversion_factor * self.box_length
                cell = [ mdi_box_length, 0.0, 0.0, 0.0, mdi_box_length, 0.0, 0.0, 0.0, mdi_box_length ]
                mdi.MDI_Send(cell, 9, mdi.MDI_DOUBLE, self.mdi_comm)
```

The `<CELL_DISPL` command requires that the engine send the driver a vector that corresponds to the displacement of the periodic cell's origin.
For `MDI_MC_Demo`, the origin of the cell is at `[-0.5*self.box_length, -0.5*self.boxlength, -0.5*self.box_length]`.
The following code will correctly respond to the `<CELL_DISPL` command:
```Python
            elif self.command == "<CELL_DISPL":
                conversion_factor = self.sigma * mdi.MDI_Conversion_factor("meter","atomic_unit_of_length")
                mdi_box_length = conversion_factor * self.box_length
                cell_displ = [ -0.5*mdi_box_length, -0.5*mdi_box_length, -0.5*mdi_box_length ]
                mdi.MDI_Send(cell_displ, 3, mdi.MDI_DOUBLE, self.mdi_comm)
```

If you rerun `mdimechanic report`, the output should indicate that all four of the above commands are now working.


## Add support for the `<ENERGY` and `>ENERGY` commands

We now need to add support for the `<ENERGY` and `>ENERGY` commands.
Adding the following lines to the `if ... else` in `mdi_node` is sufficient to support the `<ENERGY` command:
```Python
            elif self.command == "<ENERGY":
                if energy is None:
                    raise Exception('The <ENERGY command was received, but the energy is not available')
                conversion_factor = self.epsilon * mdi.MDI_Conversion_factor("joule","atomic_unit_of_energy")
                mdi_energy = conversion_factor * energy
                mdi.MDI_Send(mdi_energy, 1, mdi.MDI_DOUBLE, self.mdi_comm)
```

Supporting `>ENERGY` is a little more involved.
First, we must receive the energy from the driver and broadcast it to all MPI ranks (only `rank 0` receives any data from the driver):
```Python
            elif self.command == ">ENERGY":
                if energy is None:
                    raise Exception('The <ENERGY command was received, but the energy is not available')

                # Receive the energy from the driver
                mdi_energy = mdi.MDI_Recv(1, mdi.MDI_DOUBLE, self.mdi_comm)
                conversion_factor = 1.0 / (self.epsilon * mdi.MDI_Conversion_factor("joule","atomic_unit_of_energy"))
                mdi_energy *= conversion_factor
                
                # Broadcast the energy to all procs
                bcast_energy = np.array( [mdi_energy] )
                self.world_comm.Bcast( [bcast_energy, MPI.DOUBLE], root = 0 )
                self.delta_energy_from_driver = bcast_energy[0] - energy
```
The energy from the driver is stored in `self.delta_energy_from_driver`.
Zero the value of this variable at the beginning of the `mdi_node` function:
```Python
    def mdi_node(self, node_name, coordinates=None, energy=None):
        self.delta_energy_from_driver = 0.0
```
Note that the `>ENERGY` command doesn't affect the calculation in any way - the `self.delta_energy_from_driver` variable is not currently used anywhere else in the code.
We will address this issue in the next section.


## Add additional nodes

One of the strengths of MDI is that it provides drivers with control over the high-level program flow of MDI engines.
For example, a driver might command an engine to begin a geometry optimization, and then add an extra term to the atomic forces during each timestep of the geometry optimization.
In order for a driver to do this, the engine must be capable of responding to commands from the driver at multiple points over the course of the geometry optimization: specificaly, each time the forces are evaluated.
In MDI parlance, a point in an engine's program flow where it is capable of listening for commands from a driver is called a "node".
Engines are permitted to implement any number of nodes, each of which has a name that is defined by the engine - the MDI Standard defines a small number of names for nodes, but does not attempt to define a name for every possible node.
All node names must begin with a `@` symbol, and the first node at which an engine listens for commands must be named `@DEFAULT`.
We implemented support for the `@DEFAULT` node earlier, when we added a call to `self.mdi_node("@DEFAULT")`.

Over the course of the rest of this tutorial, we are going to work towards enabling the `MDI_MC_Demo` to facilitate a use case in which an external driver adds an additional term to the energy of each test displacement.
Furthermore, we want to implement this in a way that enables the external driver to be written in a way that is portable with respect to engine; in other words, the external driver should be capable of working with any MDI engine that supports Monte Carlo calculations, and shouldn't make any assumptions that are specific to `MDI_MC_Demo`.

To this end, we need `MDI_MC_Demo` to implement a node called `@INIT_MC`, which is one of a small number of nodes that is defined by the MDI Standard.
This node corresponds to the moment "upon initializing a new Monte Carlo simulation," and is important because it effectively allows a driver to command an engine to begin a Monte Carlo simulation.
In a sense, this may seem redundant or unnecessary for `MDI_MC_Demo`; after all, the only thing `MDI_MC_Demo` can do is run Monte Carlo simulations, so why does the driver need to specifically command it to begin a Monte Carlo simulation?
The reason we still need to implement an `@INIT_MC` node is because there are other engines that are capable of running Monte Carlo simulations, **and** molecular dynamics simulations, **and** geometry optimizations; in those cases, a driver needs to be able to specify to the engine whether it should begin a Monte Carlo simulations (by sending the `@INIT_MC` command), or a molecular dynamics simulation (by sending the `@INIT_MD` command), or a geometry optimization (by sending the `@INIT_OPTG` command).
For the purpose of enabling drivers to be designed portably, the `MDI_MC_Demo` needs to implement an `@INIT_MC` node.

Add the `@INIT_MC` node immediately after the `@DEFAULT` node, so that the first few lines of `run` are:
```Python
    def run(self):
        if self.use_mdi:
            # @DEFAULT node
            self.mdi_node("@DEFAULT", coordinates=self.coordinates)
            if self.command == "EXIT":
                return

            # @INIT_MC node
            self.mdi_node("@INIT_MC", coordinates=self.coordinates)
            if self.command == "EXIT":
                return
```

We now need `MDI_MC_Demo` to be able to listen for commands everytime it recomputes the energy.
The first time the energy is calcualted is just before the Monte Carlo iterate loop begins.
Insert the following code just before the comment that reads `Main Monte Carlo loop`:
```Python
        if self.use_mdi:

            # @ENERGY node
            self.mdi_node("@ENERGY",
                          coordinates = self.coordinates,
                          energy = total_pair_energy + tail_correction)

            if self.command == "EXIT":
                return
```
The energy is then recomputed during every iteration of the Monte Carlo loop.
Insert the following just before the comment that reads `Accept or reject the step`:
```Python
            if self.use_mdi:

                # @ENERGY node
                previous_driver_delta = self.delta_energy_from_driver
                self.mdi_node("@ENERGY",
                              coordinates=proposed_coordinates,
                              energy=total_pair_energy + tail_correction + delta_e)
                new_driver_delta = self.delta_energy_from_driver
                delta_e += new_driver_delta - previous_driver_delta

                if self.command == "EXIT":
                    return
```

Finally, there are some node-related commands that we need to support.
Add the following to the `mdi_node` `if ... else`:
```Python
            elif self.command == "@INIT_MC":
                self.target_node = "@INIT_MC"
                return

            elif self.command == "@ENERGY":
                self.target_node = "@ENERGY"
                return

            elif self.command == "@":
                self.target_node = "@"
                return

            elif self.command == "<@":
                mdi.MDI_Send(node_name, mdi.MDI_NAME_LENGTH, mdi.MDI_CHAR, self.mdi_comm)
```
The `@INIT_MC` and `@ENERGY` commands tell the engine to proceed to those particular nodes.
The `@` is only valid if the driver has previously commanded the engine to initialize a simulation (*i.e.*, by sending an `@INIT_MD`, `@INIT_MC`, or `@INIT_OPTG` command), and commands the engine to proceed to the next node, regardless of the name of the node.
The `<@` command requests that the engine send the name of the current node.

In order to ensure that the code proceeds to the correct nodes in response to one of the `@INIT_MC`, `@ENERGY`, or `@` commands from the driver, insert the following near the beginning of the `mdi_node` function, just after the line that reads `self.energy_from_driver = None`:
```Python
        if self.target_node is not None:
            if self.target_node == node_name or self.target_node == "@":
                # Reset the target node and proceed to listen for comands at this node
                self.target_node = None
            else:
                # Ignore this node completely
                return
```

Then initialize `self.target_node` to `None` at the end of the `MCSimulation` initialization function:
```Python
            # Initialize the MDI target node
            self.target_node = None
```

When an engine like `MDI_MC_Demo` is controlled by a driver, the driver code should have control over decisions like the number of iterations to run, and it should be able to decide this dynamically.
One quick-and-dirty way to enable this with our driver is to simply set `self.n_steps` to an arbitrarily large value when running with MDI, which means the engine can continue iterating until it receives an `EXIT` command.
Add the following to the end of the `MCSimulation` initialization function:
```Python
        if self.use_mdi:
            self.n_steps = 1000000000
```


## Register nodes and commands with the driver

MDI allows engines to "register" nodes and commands with the MDI Library, which enables external drivers to query the capabilities of the engine.
Because each node can potentially support a different set of commands, MDI allows the engine to register a different set of supported commands for each node.
You can register the supported nodes and commands of `MDI_MC_Demo` by inserting the following in the `MCSimulation` initialization function, just after the line that reads `mdi.MDI_Init(mdi_options)`:

```Python
        # Register MDI nodes and commands
        if self.use_mdi:
            mdi.MDI_Register_node("@DEFAULT")
            mdi.MDI_Register_command("@DEFAULT", "<CELL")
            mdi.MDI_Register_command("@DEFAULT", "<CELL_DISPL")
            mdi.MDI_Register_command("@DEFAULT", "<COORDS")
            mdi.MDI_Register_command("@DEFAULT", "@INIT_MC")
            mdi.MDI_Register_command("@DEFAULT", "EXIT")
            mdi.MDI_Register_command("@DEFAULT", "<NATOMS")
            mdi.MDI_Register_command("@DEFAULT", "<@")

            mdi.MDI_Register_node("@INIT_MC")
            mdi.MDI_Register_command("@INIT_MC", "<CELL")
            mdi.MDI_Register_command("@INIT_MC", "<CELL_DISPL")
            mdi.MDI_Register_command("@INIT_MC", "<COORDS")
            mdi.MDI_Register_command("@INIT_MC", "@ENERGY")
            mdi.MDI_Register_command("@INIT_MC", "EXIT")
            mdi.MDI_Register_command("@INIT_MC", "<NATOMS")
            mdi.MDI_Register_command("@INIT_MC", "@")
            mdi.MDI_Register_command("@INIT_MC", "<@")

            mdi.MDI_Register_node("@ENERGY")
            mdi.MDI_Register_command("@ENERGY", "<CELL")
            mdi.MDI_Register_command("@ENERGY", "<CELL_DISPL")
            mdi.MDI_Register_command("@ENERGY", "<COORDS")
            mdi.MDI_Register_command("@ENERGY", "<ENERGY")
            mdi.MDI_Register_command("@ENERGY", ">ENERGY")
            mdi.MDI_Register_command("@ENERGY", "@ENERGY")
            mdi.MDI_Register_command("@ENERGY", "EXIT")
            mdi.MDI_Register_command("@ENERGY", "<NATOMS")
            mdi.MDI_Register_command("@ENERGY", "@")
            mdi.MDI_Register_command("@ENERGY", "<@")
```

It is also a good practice to raise an error if the driver sends a command that is not supported at a specific node.
Insert the following in the `mdi_node` function, just before the comment that reads `Respond to the received command`:
```Python
            # Check if this command is supported at this node
            if self.my_rank == 0:
                if not mdi.MDI_Check_command_exists(node_name, self.command, mdi.MDI_COMM_NULL):
                    raise Exception('The following command is not supported at this node: ' + str(self.command))
```

We are now finished implementing MDI engine capabilities into the `MDI_MC_Demo` engine.
Now would be a good time to run `mdimechanic report` to confirm that the engine's features are working as expected.

In the next section, we will try controlling `MDI_MC_Demo` with a simple driver.


## Create a simple driver

From the directory where `mdimechanic.yml` is located, create a subdirectory called `test_driver`, and within that directory, create a file called `test_driver.py`.

Add the following to `test_driver.py`:

```Python
import mdi
import sys
from mpi4py import MPI

# Receive the -mdi option                                                                                                                                     
mdi_options = None
use_mdi = False
for iarg in range( len(sys.argv) ):
    if sys.argv[iarg] == "-mdi" or sys.argv[iarg] == "--mdi":
        if len(sys.argv) > iarg + 1:
            mdi_options = sys.argv[iarg+1]
            use_mdi = True
        else:
            raise Exception('Argument to -mdi option was not provided')
if not use_mdi:
    raise Exception('-mdi option was not provided')

# Initialize MDI                                                                                                                                              
mdi.MDI_Init(mdi_options)

# Establish a connection with the engine                                                                                                                      
mdi_comm = mdi.MDI_Accept_communicator()

# Get the name of the engine                                                                                                                                  
mdi.MDI_Send_command("<NAME", mdi_comm)
engine_name = mdi.MDI_Recv(mdi.MDI_NAME_LENGTH, mdi.MDI_CHAR, mdi_comm)
print("Engine name: " + str(engine_name))

# Get the number of atoms in the system                                                                                                                       
mdi.MDI_Send_command("<NATOMS", mdi_comm)
natoms = mdi.MDI_Recv(1, mdi.MDI_INT, mdi_comm)

# Initialize an MC simulation                                                                                                                                 
mdi.MDI_Send_command("@INIT_MC", mdi_comm)

start_simulation_time = MPI.Wtime()

nsteps = 1000
for i in range(nsteps):
    # Proceed to the next node                                                                                                                                
    mdi.MDI_Send_command("@", mdi_comm)

    # Request the name of the node                                                                                                                            
    mdi.MDI_Send_command("<@", mdi_comm)
    node_name = mdi.MDI_Recv(mdi.MDI_NAME_LENGTH, mdi.MDI_CHAR, mdi_comm)

    # Get the energy                                                                                                                                          
    mdi.MDI_Send_command("<ENERGY", mdi_comm)
    energy = mdi.MDI_Recv(1, mdi.MDI_DOUBLE, mdi_comm)

    # Get the coordinates                                                                                                                                     
    mdi.MDI_Send_command("<COORDS", mdi_comm)
    coords = mdi.MDI_Recv(3*natoms, mdi.MDI_DOUBLE, mdi_comm)

    # Count the number of atoms that are located at x > 0.0                                                                                                   
    count = 0
    for	iatom in range(natoms):
        if coords[3*iatom + 0] > 0.0:
            count += 1
    fraction = float(count) / float(natoms)
    print("Energy, Fraction: " + str(energy) + " " + str(fraction))

    # Add a new term to the energy                                                                                                                            
    energy += 100.0 * count

    # Send the new energy                                                                                                                                     
    mdi.MDI_Send_command(">ENERGY", mdi_comm)
    mdi.MDI_Send(energy, 1, mdi.MDI_DOUBLE, mdi_comm)


# Tell the engine to exit                                                                                                                                     
mdi.MDI_Send_command("EXIT", mdi_comm)

total_simulation_time = MPI.Wtime() - start_simulation_time
print("Simulation Time: " + str(total_simulation_time))
print("Average Iteration Time: " + str(total_simulation_time / nsteps))
```

Add the following to the end of `mdimechanic.yml`:

```
test_drivers:
  test_driver:
    script:
      - cd test_driver
      - python test_driver.py -mdi "-role DRIVER -name driver -method TCP -port 8021"
```

You can now use MDI Mechanic to run a calculation using the test driver we just created and the `MDI_MC_Demo` engine.
Execute the following command from the directory where `mdimechanic.yml` is located:
```
mdimechanic rundriver --name test_driver
```


### Copyright

Copyright (c) 2021, Taylor Barnes


#### Acknowledgements
 
Project based on the 
[Computational Molecular Science Python Cookiecutter](https://github.com/molssi/cookiecutter-cms) version 1.5.
