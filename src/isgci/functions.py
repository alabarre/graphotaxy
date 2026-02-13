"""
Anthony Labarre © 2024

Functions useful in various modules of the isgci package.
"""
# Imports ---------------------------------------------------------------------
# ----- Standard imports ------------------------------------------------------
from re import sub


def class_id_from_url(url: str) -> str:
    """Returns a class ID from the corresponding URL in ISGCI.

    :param url: the url of an ISGCI class.
    :returns: the class ID.

    >>> class_id_from_url("https://www.graphclasses.org/classes/gc_575.html")
    'gc_575'
    >>> class_id_from_url("https://www.graphclasses.org/classes/gc_575")
    'gc_575'
    """
    return url.split("/")[-1].replace(".html", "")


def prettify_name(html_class_name: str) -> str:
    """Returns a LaTeX-compatible encoding of the HTML string that encodes a graph class name in
    ISGCI.

    :param html_class_name: the name of a graph class as an HTML string
    :returns: a LaTeX-compatible encoding of text.


    >>> prettify_name("K<sub>4</sub>-free ∩ planar")
    'K_{4}-free ∩ planar'
    >>> prettify_name("")
    ''

    """
    # ignore alternative names
    html_class_name = html_class_name.split("\n")[0]

    # replace union character with U (for some reason, we need to try both
    # ways ...)
    html_class_name = (
        html_class_name.encode().replace(b"\xc3\xa2\xc2\x88\xc2\xaa", b"U").decode()
    )
    html_class_name = html_class_name.replace("∪", "U")

    # the regex's below need the ? character to avoid the "nested match issue":
    # when we have (A)(B), we want to match the parentheses surrounding A and B,
    # respectively, instead of matching the first ( with the last ) (replace
    # parentheses with sub or sup for the use cases below)

    # replace <sub>TEXT</sub> with _{TEXT}
    html_class_name = sub(r"<sub>(.*?)</sub>", r"_{\1}", html_class_name)

    # replace <sup>TEXT</sup> with ^{TEXT}
    html_class_name = sub(r"<sup>(.*?)</sup>", r"\^{\1}", html_class_name)

    # replace <span class="complement">TEXT</span> with co(TEXT)
    html_class_name = sub(
        r'<span class="complement">(.*?)</span>', r"co(\1)", html_class_name
    )

    # replace signs
    html_class_name = html_class_name.replace("&gt;", ">")
    html_class_name = html_class_name.replace("&lt;", "<")

    return html_class_name
