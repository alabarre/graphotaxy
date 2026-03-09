"""
Anthony Labarre © 2024-2026

Variables useful in various modules of the ISGCI package.
"""
# Imports -----------------------------------------------------------------------------------------
# ----- Standard imports --------------------------------------------------------------------------
from os.path import dirname, join

# Variables ---------------------------------------------------------------------------------------
# Misc paths --------------------------------------------------------------------------------------
ROOT = dirname(__file__)
ISGCI_DIR = join(ROOT, "isgci_db")
PATHS = {
    "database": join(ROOT, "isgci_db"),
    "classes": join(ROOT, "isgci_db", "classes"),
    "isgci_inclusion_graph": join(ROOT, "isgci_inclusion_graph.json"),
    "isgci_equivalences": join(ROOT, "isgci_equivalences.json"),
    "isgci_ids_to_names": join(ROOT, "isgci_ids_to_names.json"),
    "isgci_recognition_statuses": join(ROOT, "isgci_ids_to_recognition_statuses.json"),
}

# Other variables ---------------------------------------------------------------------------------
EASY, HARD, OPEN = "+-?"  # categories for problems in ISGCI
