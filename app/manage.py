#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys

# Default django server IP and Port
_DJANGO_IP = '0.0.0.0'
_DJANGO_PORT = '8000'

def main():
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    new_arg = sys.argv + [_DJANGO_IP + ':' + _DJANGO_PORT]
    execute_from_command_line(new_arg)

if __name__ == '__main__':
    main()
