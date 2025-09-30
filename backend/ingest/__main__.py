from __future__ import annotations

import argparse
from pathlib import Path

from backend.init_db import init_db

from .manager import IngestManager


def main() -> None:
    parser = argparse.ArgumentParser(description="Run ingestion cycle")
    parser.add_argument("--config", type=Path, default=Path("config/sources.yaml"))
    args = parser.parse_args()

    init_db()
    manager = IngestManager(args.config)
    manager.run_once()


if __name__ == "__main__":
    main()
