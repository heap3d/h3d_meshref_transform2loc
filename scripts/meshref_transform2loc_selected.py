#!/usr/bin/python
# ================================
# (C)2026 Dmytro Holub
# heap3d@gmail.com
# --------------------------------
# EMAG
# modo python
# create locator at meshref, parent in-place meshef to a new locator for selected meshrefs with nonzero transforms

import modo
import modo.constants as c
import lx

from h3d_utilites.scripts.h3d_utils import get_user_value

from scripts.meshref_transform2loc import (
    USERVAL_NAME_TOLERANCE,
    get_nonzero_items,
    get_meshrefs,
    get_children,
    get_root_children,
    meshref_transform_to_locator,
    execution_time_alarm,
    select_if_exists,
)


@execution_time_alarm()
def main():
    TOLERANCE = get_user_value(USERVAL_NAME_TOLERANCE)

    selected_items = modo.Scene().selectedByType(c.LOCATOR_TYPE, superType=True)

    meshrefs = get_meshrefs(selected_items)
    nonzero_meshrefs = get_nonzero_items(meshrefs, TOLERANCE)

    processed_items: set[modo.Item] = set()
    for item in nonzero_meshrefs:
        if item in processed_items:
            continue

        siblings: set[modo.Item] = set()

        parent = item.parent
        children = get_children(parent, False) if parent else get_root_children(False)
        siblings.update([child for child in children if child in nonzero_meshrefs])

        meshref_transform_to_locator(siblings, TOLERANCE)

        processed_items.update(siblings)

    print(f'{len(processed_items)} item processed.')
    print('\n'.join([item.name for item in processed_items]))

    if not processed_items:
        return

    select_if_exists(processed_items)
    lx.eval('transform.reset all')

    parents = [item.parent for item in processed_items if item.parent]
    select_if_exists(parents)


if __name__ == '__main__':
    main()
