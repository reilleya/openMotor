from setuptools import setup, find_packages
from uilib.fileIO import appVersionStr

try:
    from pyqt_distutils.build_ui import build_ui
    cmdclass = {'build_ui': build_ui}
except ImportError:
    build_ui = None  # user won't have pyqt_distutils when deploying
    cmdclass = {}

setup(
    name='openMotor',
    version=appVersionStr,
    license='GPLv3',
    packages=find_packages(),
    url='https://github.com/reilleya/openMotor',
    description='An open-source internal ballistics simulator for rocket motor experimenters',
    long_description=open('README.md').read(),
    cmdclass=cmdclass
)