import logging
import sys
from pathlib import Path

logger = logging.getLogger(__name__)


def verify_directory_structure() -> bool:
    """Verify that all required directories and files exist.

    Returns:
        bool: True if all required paths exist, False otherwise
    """
    base_dir = Path(__file__).parent
    required_paths = [
        'src/your_project_name/__init__.py',
        'src/your_project_name/api/__init__.py',
        'src/your_project_name/core/__init__.py',
        'src/your_project_name/services/__init__.py',
        'src/your_project_name/utils/__init__.py',
        'tests/__init__.py',
        'tests/unit/__init__.py',
        'tests/integration/__init__.py',
    ]

    missing_paths = [path for path in required_paths if not (base_dir / path).exists()]

    if missing_paths:
        logger.error('Missing required files/directories:')
        for path in missing_paths:
            logger.error('  - %s', path)
        return False

    logger.info('✅ All required directories and files are present!')
    return True


if __name__ == '__main__':
    success = verify_directory_structure()
    sys.exit(0 if success else 1)
