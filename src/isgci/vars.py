"""
Anthony Labarre © 2024

Variables useful in various modules of the isgci package.
"""
# Imports ---------------------------------------------------------------------
# ----- Standard imports ------------------------------------------------------
from os.path import dirname, join


# Variables -------------------------------------------------------------------
# Misc paths ------------------------------------------------------------------
ROOT = dirname(__file__)
ISGCI_DIR = join(ROOT, "isgci_db")
PATHS = {
    "database": join(ROOT, "isgci_db"),
    "classes": join(ROOT, "isgci_db", "classes"),
#    "isgci_inclusion_graph": join(ROOT, "isgci_inclusion_graph.pickle"),
    "isgci_inclusion_graph": join(ROOT, "isgci_inclusion_graph.json"),
    "isgci_equivalences": join(ROOT, "isgci_equivalences.pickle"),
    "isgci_ids_to_names": join(ROOT, "isgci_ids_to_names.json"),
}

# Other variables -------------------------------------------------------------
EASY, HARD, OPEN = "+-?"  # categories for problems in ISGCI
