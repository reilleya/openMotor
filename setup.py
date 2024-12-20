from setuptools import setup, find_packages, Extension
from uilib.fileIO import appVersionStr
from Cython.Build import cythonize
import numpy
import multiprocessing

try:
    from pyqt_distutils.build_ui import build_ui
    cmdclass = {'build_ui': build_ui}
except ImportError:
    print('pyqt_distutils not found, build_ui command will be unavailable')
    build_ui = None  # user won't have pyqt_distutils when deploying
    cmdclass = {}

extensions = [
    Extension(
        "mathlib._find_perimeter_cy",  # Full module path
        ["mathlib/_find_perimeter_cy.pyx"],  # File location
        define_macros=[('NPY_NO_DEPRECATED_API', 'NPY_1_7_API_VERSION')],
        include_dirs=[numpy.get_include()]
    )
]

setup(
    name='openMotor',
    version=appVersionStr,
    license='GPLv3',
    ext_modules=cythonize(extensions, 
            nthreads = multiprocessing.cpu_count(), 
            compiler_directives={'language_level': 3}
            ),
    packages=find_packages(),
    url='https://github.com/reilleya/openMotor',
    description='An open-source internal ballistics simulator for rocket motor experimenters',
    long_description=open('README.md').read(),
    cmdclass=cmdclass
)