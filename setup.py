from setuptools import setup, Extension
from Cython.Build import cythonize

extensions = [
    Extension("skyscraper.grid_manager", ["skyscraper/grid_manager.pyx"]),
    Extension("skyscraper.backtrack", ["skyscraper/backtrack.pyx"]),
    Extension("skyscraper.pre_compute", ["skyscraper/pre_compute.pyx"]),
    Extension("skyscraper.game", ["skyscraper/game.pyx"]),
    Extension("skyscraper.main", ["skyscraper/main.pyx"]),
]

setup(
    ext_modules=cythonize(extensions, language_level="3")
)
