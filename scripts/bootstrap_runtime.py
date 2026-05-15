from __future__ import annotations

import logging
import sys
from pathlib import Path

from hy3dpaint.bootstrap import (
    apply_torchvision_compatibility_fix,
    prepare_runtime_environment,
)


def main() -> int:
    project_root = Path(__file__).resolve().parents[1]
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    logger = logging.getLogger("hy3d.bootstrap")

    apply_torchvision_compatibility_fix(logger=logger)
    prepare_runtime_environment(project_root, sys.executable, logger=logger)
    logger.info("Runtime bootstrap completed for %s", project_root)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
