from setuptools import setup, find_packages
from uilib.fileIO import appVersionStr
# import build_ui
try:
    from pyqt_distutils.build_ui import build_ui
    cmdclass = {'build_ui': build_ui}
except ImportError:
    build_ui = None  # user won't have pyqt_distutils when deploying
    cmdclass = {}

requirements = list(open('requirements.txt').read().splitlines())

setup(
    name='openMotor',
    version=appVersionStr,
    packages=find_packages(),
    url='https://github.com/reilleya/openMotor',
    install_requires=requirements,
    long_description=open('README.md').read(),
    cmdclass=cmdclass
)