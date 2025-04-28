from setuptools import setup, find_packages

setup(
    name='serialmidi-gui-app',
    version='0.1.0',
    author='Your Name',
    author_email='your.email@example.com',
    description='A Serial MIDI bridge application with a GUI',
    packages=find_packages(where='src'),
    package_dir={'': 'src'},
    install_requires=[
        'PyQt5',  # or 'PySide2' if you prefer
        'rtmidi',
        'pyserial',
    ],
    entry_points={
        'console_scripts': [
            'serialmidi-gui-app=gui:main',  # Assuming you will define a main function in gui.py
        ],
    },
)