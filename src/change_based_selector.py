"""
change_based_selector.py: Implements Method B (Change-Based Selection).
Selects tests associated with the changed module and explicitly declared dependent modules.
"""
import time
from typing import Dict, List, Set, Tuple


def select_change_based_tests(
    changed_module: str,
    test_module_map: Dict[str, str],
    dependencies: Dict[str, List[str]]
) -> Tuple[List[str], float]:
    """
    Selects tests associated with changed module and its dependent modules.
    Returns:
        (selected_test_ids, selection_overhead_sec)
    """
    start_time = time.perf_counter()

    # Affected modules = changed_module + modules that depend on changed_module + direct dependencies
    affected_modules: Set[str] = {changed_module}

    # Downstream dependencies (modules that depend on changed_module)
    for mod, deps in dependencies.items():
        if changed_module in deps:
            affected_modules.add(mod)

    # Upstream dependencies (modules changed_module depends on)
    for dep in dependencies.get(changed_module, []):
        affected_modules.add(dep)

    selected_tests = [
        test_id for test_id, mod in test_module_map.items()
        if mod in affected_modules
    ]

    overhead = time.perf_counter() - start_time
    return selected_tests, overhead
