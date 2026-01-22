"""
Increment Counter Script
Used in the AOC extraction loop to advance the counter.
"""

def increment(n: int) -> int:
    """Return n + 1."""
    return n + 1

def main(input_1) -> int:
    """Entry point for NormCode execution."""
    # Handle string input (MVP may pass '1' instead of 1)
    if isinstance(input_1, str):
        input_1 = int(input_1)
    return increment(input_1)

