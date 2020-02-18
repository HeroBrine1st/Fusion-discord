#!/usr/bin/env python
import os
import sys


def main():
    os.environ.setdefault('FUSION_SETTINGS_MODULE', 'PASTEFUSIONSETTINGSHERE')
    try:
        from fusion.management import execute_from_command_line
    except ImportError as e:
        raise ImportError(
            "Couldn't import Fusion. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from e
    execute_from_command_line(sys.argv)


if __name__ == "__main__":
    main()
