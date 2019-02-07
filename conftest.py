import pytest


def pytest_collection_modifyitems(session, config, items):
    """
    Called after collection has been performed, may filter or re-order
    the items in-place. Use with decorator:
    @pytest.mark.only
    """
    found_only_marker = False
    for item in items.copy():
        if item.get_closest_marker('only'):
            if not found_only_marker:
                items.clear()
                found_only_marker = True
            items.append(item)
