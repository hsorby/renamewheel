============
renamewheel
============

A simple command-line utility to rename Linux Python wheels based on their platform and ABI tag to be compliant with a specific ``manylinux`` standard.

The Problem
-----------

When building Python wheels on modern Linux distributions, the resulting wheel file is often tagged with a generic platform tag like ``linux_x86_64``. While technically correct for the build environment, this tag is not recognized as a compatible distribution package by tools like ``pip`` when installing on other Linux systems.

The standard for portable Linux wheels is the ``manylinux`` tag (e.g., ``manylinux_2_34_x86_64``), which guarantees compatibility with a wide range of distributions by linking against an older, stable set of core libraries (defined by the `manylinux PEPs <https://www.python.org/dev/peps/pep-0513/>`_).

``renamewheel`` provides a straightforward way to rename a wheel file from a ``linux_*`` tag to the appropriate ``manylinux_*`` tag corresponding to the system's glibc version, making it suitable for distribution on platforms like PyPI.

Installation
------------

The package can be installed from PyPI using pip:

.. code-block:: bash

   pip install renamewheel

This will install the package and make the ``renamewheel`` command-line application available in your environment.

Usage
-----

The application takes the path to a wheel file and renames it.

.. code-block:: text

   usage: renamewheel [-h] [-v] [-w WORKING_DIR] WHEEL_FILE

   Rename Linux Python wheels based on their ABI tag.

   positional arguments:
     WHEEL_FILE            Path to wheel file.

   options:
     -h, --help            show this help message and exit
     -v, --verbose         Print out messages to the console.
     -w WORKING_DIR, --working-dir WORKING_DIR
                           Copy the renamed wheel to this directory.

**Arguments & Options**

``WHEEL_FILE``
  The path to the ``.whl`` file that needs to be renamed. This is a required argument.

``-h, --help``
  Shows the help message and exits.

``-v, --verbose``
  Enables verbose output, printing messages about the renaming process to the console.

``-w WORKING_DIR, --working-dir WORKING_DIR``
  Specifies a directory where the newly renamed wheel file will be copied. If this option is not provided, the original wheel is renamed in place.

Example
-------

Given a wheel file named ``robotpy_hal-2025.3.2.3-cp313-cp313-linux_x86_64.whl``.

Running the command:

.. code-block:: bash

   renamewheel robotpy_hal-2025.3.2.3-cp313-cp313-linux_x86_64.whl

Will rename it to (assuming the system glibc version corresponds to ``manylinux_2_34``):

.. code-block:: text

   robotpy_hal-2025.3.2.3-cp313-cp313-manylinux_2_34_x86_64.whl

Exit Codes
----------

The ``renamewheel`` application uses the following exit codes to indicate success or specific error conditions, which can be useful in scripts and CI/CD pipelines.

* **0**: ``EXIT_SUCCESS`` - The operation completed successfully.
* **1**: ``EXIT_WRONG_PLATFORM`` - The script was run on a non-Linux platform.
* **2**: ``EXIT_FILE_NOT_FOUND`` - The specified ``WHEEL_FILE`` does not exist.
* **3**: ``EXIT_NOT_PLATFORM_WHEEL`` - The specified wheel is not a Linux platform wheel (e.g., it's a pure Python wheel or for another OS).
* **4**: ``EXIT_OUTPUT_DIRECTORY_NOT_FOUND`` - The directory specified with ``-w`` or ``--working-dir`` does not exist.
