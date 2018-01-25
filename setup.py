import distutils
from distutils.core import setup, Extension

import sdss3tools
import os

sdss3tools.setup(
    name = 'ics_templateGUI',
    description = "Toy SDSS-3 actor.",
    )

