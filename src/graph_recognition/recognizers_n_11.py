"""
Anthony Labarre © 2025-2026

O(n^11) algorithms.

"""
# Imports -----------------------------------------------------------------------------------------
# ----- Standard imports --------------------------------------------------------------------------
import os

# ----- My imports --------------------------------------------------------------------------------
from graph_recognition.recognizers_utils import (
    current_module_recognizers, )

# ----- Third-party imports -----------------------------------------------------------------------

# Recognizers -------------------------------------------------------------------------------------


# This code segment must always be at the END of a recognizer file --------------------------------
RECOGNIZERS = current_module_recognizers(
    ".".join(
        [
            os.path.basename(os.path.dirname(__file__)),
            os.path.basename(__file__).removesuffix(".py"),
        ]
    )
)
# -------------------------------------------------------------------------------------------------
