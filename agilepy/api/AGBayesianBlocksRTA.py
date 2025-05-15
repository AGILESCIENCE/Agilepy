import logging
from pathlib import Path
import sys

# Add BBrta module path to the system path
BBRTA_PATH = Path(__file__).parent / "../external_packages/BBrta/python_code"
sys.path.insert(0, str(BBRTA_PATH))

try:
    from agile_bblocks import AGILE_BBlocks
except ImportError as e:
    logging.error(f"Unable to import BBrtaProcessor: {e}")
    BBrtaProcessor = None

class AGBBrta(AGILE_BBlocks):
    """
    Wrapper for the Bayesian Blocks Real-Time Analysis (RTA) module.
    Provides an interface to process data using Bayesian Blocks segmentation.
    """

    def __init__(self):
        """
        Initialize the AGILE_BBlocks class.
        """
        super().__init__()