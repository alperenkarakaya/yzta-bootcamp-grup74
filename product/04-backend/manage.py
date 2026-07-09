#!/usr/bin/env python
"""Django yönetim aracı."""
import os
import sys
from pathlib import Path

from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parent / ".env")


def main():
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Django bulunamadı. Sanal ortam etkin mi? `pip install -r requirements.txt`"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == "__main__":
    main()
