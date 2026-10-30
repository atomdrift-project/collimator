"""Stable, dependency-free exception types shared by worker processes.

Keep transport types separate from implementation modules that long-lived
parents may have imported before a worker starts with updated source code.
"""


class FactProfileError(ValueError):
    """A report's fact profile cannot supply every feature in the layout."""
