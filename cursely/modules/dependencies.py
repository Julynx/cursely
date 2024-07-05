"""
Contains methods to calculate the dependencies of mods.
"""

from itertools import chain
from multiprocessing import Pool
from typing import Union

from .mods import Mod


def _dependencies_wrapper(mod: Mod) -> Union[set[Mod], int]:
    """
    Wrapper for the mod_dependencies function.

    Args:
        mod (Mod): The mod to get the dependencies for.

    Returns:
        set: The dependencies of the mod. {-1} in case of error.
    """
    try:
        dependencies = mod.dependencies
        print("*", end="", flush=True)
        return dependencies
    except ValueError:
        print("-", end="", flush=True)
        return {-1}


def calculate_dependencies(mods: list[Mod]) -> set[Mod]:
    """
    Calculate the dependencies of a list of mods.

    Args:
        mods (list): A list of mods.

    Returns:
        set: The dependencies of the mods.
                Will catch any errors and print error messages.
    """
    print("Calculating dependencies...")
    dependencies = []

    with Pool() as pool:
        dependencies.extend(pool.map(_dependencies_wrapper, mods))

    print()

    dependencies = set(chain.from_iterable(dependencies))

    if -1 in dependencies:
        raise ValueError("Failed to get dependencies.")

    return dependencies
