"""
MDI_MC_Demo.py
A very basic Monte Carlo code intended to be used as part of an MDI engine tutorial.

Handles the primary functions
"""


from mpi4py import MPI
import numpy as np

class MCSimulation:
    def __init__(self):

        #-------------------
        # MPI Initialization
        #-------------------

        self.start_simulation_time = MPI.Wtime()
        self.total_energy_time = 0.0
        self.total_decision_time = 0.0

        self.world_comm = MPI.COMM_WORLD
        self.world_size = self.world_comm.Get_size()
        self.my_rank = self.world_comm.Get_rank()

        #----------------------
        # Adjustable Parameters
        #----------------------

        # Temperature of the simulation in Kelvin
        self.temperature = 120.0

        # Particle mass in kilograms
        self.mass = 39.948 * 1.66054e-27

        # System density in kg / m^3
        self.density = 1500.0

        # Lennard-Jones parameters, in SI units
        self.sigma = 3.4e-10
        self.epsilon = 1.65e-21

        # Distance cutoff for the Lennard-Jones potential, in meters
        self.distance_cutoff = 3.0 * self.sigma

        # Maximum test displacement, in meters
        self.max_displacement = 0.1 * self.sigma

        self.n_steps = 100
        self.freq = 10
        self.num_particles = 100
        self.tune_displacement = True
        self.build_method = 'random'

        #-------------------------
        # Fixed/Derived Parameters
        #-------------------------

        # Boltzmann constant in SI units
        self.boltzmann = 1.38064852e-23

        self.reduced_temperature = self.temperature / (self.epsilon / self.boltzmann)
        self.reduced_density = self.density / (self.mass / self.sigma**3)
        self.reduced_max_displacement = self.max_displacement / self.sigma
        self.reduced_simulation_cutoff = self.distance_cutoff / self.sigma

        self.box_length = np.cbrt(self.num_particles / self.reduced_density)
        self.beta = 1.0 / self.reduced_temperature
        self.reduced_simulation_cutoff2 = np.power(self.reduced_simulation_cutoff, 2)

        #--------------------------
        # Coordinate initialization
        #--------------------------

        if self.my_rank == 0:
            self.coordinates = self.generate_initial_state(method=self.build_method, num_particles=self.num_particles, box_length=self.box_length)
        else:
            self.coordinates = np.empty([self.num_particles, 3])
        self.world_comm.Bcast( [self.coordinates, MPI.DOUBLE], root = 0 )


    def generate_initial_state(self, method='random', file_name=None, num_particles=None, box_length=None):
        """
        Function generates initial coordinates for a LJ fluid simulation

        This function can generate coordintes either from a file (NIST LJ Fluid Configurations) or from
        a random configuration

        Parameters
        ----------

        method : str
            String the method to use to build the initial configuration for the LJ fluid simulation. Possible values are 'random'  or 'file' (Default value is 'random')
        file_name : str
            String of the the filename containing the initial starting coordinates. Only required when using the 'fille' method (Default value = None)
        num_particles : int
            Number of particules to use when populating the simualtion box with the 'random' method (Default value = None)
        box_length : float
            Size of one vertices of the simulation box. (Default value = None)

        Returns
        -------

        coordinates : np.array
            A (num_particles x 3) numpy array containing the coordinates of each LJ particle.

        Examples
        --------

        >>> generate_initial_state('random', num_particles = 1000, box_length = 20)
        array([[ 1.10202674,  4.24975121, -5.03322129],
            [ 9.13676284,  4.78807621, -8.26008762],
            [ 6.24720765, -7.17769567,  9.61620896],
            ...,
            [-3.47864571,  2.32867699, -1.31176807],
            [ 1.3302019 , -3.4160087 , -1.34698966],
            [ 0.56410479, -1.2309513 ,  4.71009776]])
        """


        if method == 'random':

            np.random.seed(seed=1)
            coordinates = (0.5 - np.random.rand(num_particles, 3)) * box_length

        elif method == 'file':

            coordinates = np.loadtxt(file_name, skiprows=2, usecols=(1,2,3))

        return coordinates


    def lennard_jones_potential(self, rij2):
        """
        Function evaluates the unitless LJ potential given a squared distance

        Parameters
        ----------
        rij2 : float
            Distance squared between two particles

        Returns
        -------

        float
            Unitless LJ potential energy
        """
        # This function computes the LJ energy between two particles

        sig_by_r6 = np.power(1 / rij2, 3)
        sig_by_r12 = np.power(sig_by_r6, 2)
        return 4.0 * (sig_by_r12 - sig_by_r6)


    def calculate_tail_correction(self, box_length, cutoff, number_particles):
        """
        This function computes the standard tail energy correction for the LJ potential

        Parameters
        ----------
        box_length : float/int
            length of simulation box
        cutoff: float/int
            the cutoff for the tail energy truncation
        num_particles: int
            number of particles

        Return
        ------
        e_correction: float
            tail correction of energy
        """


        volume = np.power(box_length, 3)
        sig_by_cutoff3 = np.power(1.0 / cutoff, 3)
        sig_by_cutoff9 = np.power(sig_by_cutoff3, 3)
        e_correction = sig_by_cutoff9 - 3.0 * sig_by_cutoff3

        e_correction *= 8.0 / 9.0 * np.pi * number_particles / volume * number_particles

        return e_correction


    def minimum_image_distance(self, r_i, r_j, box_length):
        # This function computes the minimum image distance between two particles

        rij = r_i - r_j
        rij = rij - box_length * np.round(rij / box_length)
        rij2 = np.dot(rij, rij)
        return rij2


    def get_particle_energy(self, coordinates, box_length, i_particle, cutoff2):

        """
        This function computes the minimum image distance between two particles

        Parameters
        ----------
        r_i: list/array
            the potitional vection of the particle i
        r_j: list/array
            the potitional vection of the particle j
        box_length : float/int
            length of simulation box

        Return
        ------
        rij2: float
            the square of the shortest distance between the two particles and their images
        """

        e_total = 0.0

        i_position = coordinates[i_particle]

        particle_count = len(coordinates)

        for j_particle in range(self.my_rank, particle_count, self.world_size):

            if i_particle != j_particle:

                j_position = coordinates[j_particle]

                rij2 = self.minimum_image_distance(i_position, j_position, box_length)

                if rij2 < cutoff2:
                    e_pair = self.lennard_jones_potential(rij2)
                    e_total += e_pair

        # Sum the energy across all ranks
        e_single = np.array( [e_total] )
        e_summed = np.zeros( 1 )
        self.world_comm.Reduce( [e_single, MPI.DOUBLE], [e_summed, MPI.DOUBLE], op = MPI.SUM, root = 0 )

        return e_summed[0]


    def calculate_total_pair_energy(self, coordinates, box_length, cutoff2):
        e_total = 0.0
        particle_count = len(coordinates)

        for i_particle in range(particle_count):
            for j_particle in range(i_particle):

                r_i = coordinates[i_particle]
                r_j = coordinates[j_particle]
                rij2 = self.minimum_image_distance(r_i, r_j, box_length)
                if rij2 < cutoff2:
                    e_pair = self.lennard_jones_potential(rij2)
                    e_total += e_pair

        return e_total


    def accept_or_reject(self, delta_e, beta):
        """Accept or reject a move based on the energy difference and system \
        temperature.

        This function uses a random numbers to adjust the acceptance criteria.

        Parameters
        ----------
        delta_e : float
            The difference between the proposed and current energies.
        beta : float
            The inverse value of the reduced temperature.

        Returns
        -------
        accept : booleen
            Either a "True" or "False" to determine whether to reject the trial.
        """
        # This function accepts or reject a move given the
        # energy difference and system temperature

        if delta_e < 0.0:
            accept = True

        else:
            random_number = np.random.rand(1)
            p_acc = np.exp(-beta * delta_e)

            if random_number < p_acc:
                accept = True
            else:
                accept = False

        return accept


    def adjust_displacement(self, n_trials, n_accept, max_displacement):
        """Change the acceptance criteria to get the desired rate.

        When the acceptance rate is too high, the maximum displacement is adjusted \
        to be higher.
        When the acceptance rate is too low, the maximum displacement is \
        adjusted lower.

        Parameters
        ----------
        n_trials : integer
            The number of trials that have been performed when the function is \
             initiated.
        n_accept : integer
            The current number of accepted trials when the function is initiated.
        max_displacement : float
            The specified maximum value for the displacement of the trial.

        Returns
        -------
        max_displacement : float
            The adjusted displacement based on the acceptance rate.
        n_trials : integer, 0
            The new number of trials.
        n_accept : integer, 0
            The new number of trials.
        """
        acc_rate = float(n_accept) / float(n_trials)
        if (acc_rate < 0.38):
            max_displacement *= 0.8

        elif (acc_rate > 0.42):
            max_displacement *= 1.2

        n_trials = 0
        n_accept = 0

        return max_displacement, n_trials, n_accept


    def run(self):

        total_pair_energy = self.calculate_total_pair_energy(self.coordinates, self.box_length, self.reduced_simulation_cutoff2)
        tail_correction = self.calculate_tail_correction(self.box_length, self.reduced_simulation_cutoff, self.num_particles)

        n_trials = 0
        n_accept = 0

        #----------------------
        # Main Monte Carlo Loop
        #----------------------

        for i_step in range(self.n_steps):

            if self.my_rank == 0:
                n_trials += 1

                i_particle = np.random.randint(self.num_particles)
                i_particle_buf = np.array( [i_particle], 'i' )

                random_displacement = (2.0 * np.random.rand(3) - 1.0) * self.reduced_max_displacement
            else:
                i_particle_buf = np.empty( 1, 'i' )
                random_displacement = np.empty( 3 )
            self.world_comm.Bcast( [i_particle_buf, MPI.INT], root = 0 )
            i_particle = i_particle_buf[0]
            self.world_comm.Bcast( [random_displacement, MPI.DOUBLE], root = 0 )
            self.world_comm.Bcast( [self.coordinates, MPI.DOUBLE], root = 0 )

            start_energy_time = MPI.Wtime()
            current_energy = self.get_particle_energy(self.coordinates, self.box_length, i_particle, self.reduced_simulation_cutoff2)
            self.total_energy_time += MPI.Wtime() - start_energy_time

            proposed_coordinates = self.coordinates.copy()
            proposed_coordinates[i_particle] += random_displacement
            proposed_coordinates -= self.box_length * np.round(proposed_coordinates / self.box_length)

            start_energy_time = MPI.Wtime()
            proposed_energy = self.get_particle_energy(proposed_coordinates, self.box_length, i_particle, self.reduced_simulation_cutoff2)
            self.total_energy_time += MPI.Wtime() - start_energy_time

            # Accept or reject the step
            if self.my_rank == 0:
                start_decision_time = MPI.Wtime()

                delta_e = proposed_energy - current_energy

                accept = self.accept_or_reject(delta_e, self.beta)

                if accept:

                    total_pair_energy += delta_e
                    n_accept += 1
                    self.coordinates[i_particle] += random_displacement

                total_energy = (total_pair_energy + tail_correction) / self.num_particles

                if np.mod(i_step + 1, self.freq) == 0:

                    print(total_energy)

                    if self.tune_displacement:
                        self.reduced_max_displacement, n_trials, n_accept = self.adjust_displacement(n_trials, n_accept, self.reduced_max_displacement)

                self.total_decision_time += MPI.Wtime() - start_decision_time

        if self.my_rank == 0:
            print("Total simulation time: " + str( MPI.Wtime() - self.start_simulation_time ) )
            print("    Energy time:       " + str( self.total_energy_time ) )
            print("    Decision time:     " + str( self.total_decision_time ) )



if __name__ == "__main__":
    simulation = MCSimulation()
    simulation.run()
