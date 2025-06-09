#!/usr/bin/python
# ================================
# (C)2025 Dmytro Holub
# heap3d@gmail.com
# --------------------------------
# EMAG
# modo python
# select meshrefs with nonzero transforms

import modo
import modo.constants as c

from h3d_utilites.scripts.h3d_utils import get_user_value

from scripts.meshref_transform2loc import USERVAL_NAME_TOLERANCE, get_nonzero_items, get_meshrefs


def main():
    TOLERANCE = get_user_value(USERVAL_NAME_TOLERANCE)

    meshrefs = get_meshrefs(modo.Scene().items(itype=c.LOCATOR_TYPE, superType=True))
    nonzero_meshrefs = get_nonzero_items(meshrefs, TOLERANCE)

    modo.Scene().deselect()
    for item in nonzero_meshrefs:
        item.select()


if __name__ == '__main__':
    main()
