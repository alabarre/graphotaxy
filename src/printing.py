"""
Anthony Labarre © 2026

Functions related to printing text.

"""
# Functions ---------------------------------------------------------------------------------------
def underlined(message: str) -> str:
    """
    Returns an underlined version of a message.

    >>> print(underlined("Hello!"))
    Hello!
    ------

    :param message: any text
    :return: the input text, underlined
    """
    return "\n".join([message, len(message) * "-"])
