"""
Anthony Labarre © 2025-2026

O(n^9) algorithms.

"""
# Imports -----------------------------------------------------------------------------------------
# ----- Standard imports --------------------------------------------------------------------------
import os

# ----- Third-party imports -----------------------------------------------------------------------

# ----- My imports --------------------------------------------------------------------------------
from graph_recognition.recognizers_utils import (
    current_module_recognizers, )

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
