import sys
from pathlib import Path

# Add parent directory to path to allow imports
sys.path.append(str(Path(__file__).parent.parent.parent))

from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()
