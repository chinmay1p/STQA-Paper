"""
random_selector.py: Implements Method C (Random Selection).
Randomly selects test subsets of size K using deterministic seeds.
"""
import random
import time
from typing import List, Tuple


def select_random_tests(
    all_tests: List[str],
    budget_count: int,
    seed: int
) -> Tuple[List[str], float]:
    """
    Selects a random subset of tests of size budget_count using fixed seed.
    Returns:
        (selected_test_ids, selection_overhead_sec)
    """
    start_time = time.perf_counter()
    rng = random.Random(seed)
    
    k = max(1, min(len(all_tests), int(budget_count)))
    selected = rng.sample(all_tests, k)

    overhead = time.perf_counter() - start_time
    return selected, overhead
