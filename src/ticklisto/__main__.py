"""
Module entry point for the Tick Listo application.
Allows running the application as a module with `python -m ticklisto`.
"""

from .cli.ticklisto_cli import main

if __name__ == "__main__":
    main()