"""
MDI_MC_Demo
A very basic Monte Carlo code intended to be used as part of an MDI engine tutorial.
"""

# Add imports here
from .MDI_MC_Demo import *

# Handle versioneer
from ._version import get_versions
versions = get_versions()
__version__ = versions['version']
__git_revision__ = versions['full-revisionid']
del get_versions, versions
