#!/usr/bin/python
# ================================
# (C)2025 Dmytro Holub
# heap3d@gmail.com
# --------------------------------
# EMAG
# modo python
# create locator at meshref, parent in-place meshef to a new locator

from typing import Iterable

import modo
import modo.constants as c
import lx

from h3d_utilites.scripts.h3d_utils import parent_items_to, get_parent_index, get_user_value, is_visible


Transforms = tuple[modo.Vector3, modo.Vector3, modo.Vector3]

LOCATOR_SUFFIX = ' loc'

USERVAL_NAME_TOLERANCE = 'h3d_mtl_zero_treshold'


def main():
    TOLERANCE = get_user_value(USERVAL_NAME_TOLERANCE)

    meshrefs = get_meshrefs(modo.Scene().items(itype=c.LOCATOR_TYPE, superType=True))
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

    modo.Scene().deselect()
    for item in processed_items:
        item.select()

    lx.eval('transform.reset all')


def get_meshrefs(items: Iterable) -> list[modo.Item]:
    if not items:
        return []

    return [item for item in items if is_meshref(item)]


def is_meshref(item: modo.Item) -> bool:
    if not item:
        return False

    if not item.id:
        print(f'{item.name=} has no id')
        return False

    return True if ':' in item.id else False


def get_nonzero_items(items: Iterable[modo.Item], tolerance: float) -> list[modo.Item]:
    return [
        item
        for item in items
        if not is_zero_transforms(item, tolerance)
    ]


def is_zero_transforms(item: modo.Item, tolerance: float) -> bool:
    pos, rot, scl = get_transforms(item)

    if not pos.equals(modo.Vector3(), tolerance):
        return False

    if not rot.equals(modo.Vector3(), tolerance):
        return False

    return scl.equals(modo.Vector3(1, 1, 1), tolerance)


def get_transforms(item: modo.Item) -> Transforms:
    pos = modo.Vector3()
    pos.x = lx.eval(f'transform.channel pos.X ? item:{{{item.id}}}')
    pos.y = lx.eval(f'transform.channel pos.Y ? item:{{{item.id}}}')
    pos.z = lx.eval(f'transform.channel pos.Z ? item:{{{item.id}}}')
    rot = modo.Vector3()
    rot.x = lx.eval(f'transform.channel rot.X ? item:{{{item.id}}}')
    rot.y = lx.eval(f'transform.channel rot.Y ? item:{{{item.id}}}')
    rot.z = lx.eval(f'transform.channel rot.Z ? item:{{{item.id}}}')
    scl = modo.Vector3()
    scl.x = lx.eval(f'transform.channel scl.X ? item:{{{item.id}}}')
    scl.y = lx.eval(f'transform.channel scl.Y ? item:{{{item.id}}}')
    scl.z = lx.eval(f'transform.channel scl.Z ? item:{{{item.id}}}')

    return (pos, rot, scl)


def get_children(item: modo.Item, visible_only: bool) -> list[modo.Item]:
    if not item:
        return []

    if visible_only:
        return [i for i in item.children() if is_visible(i)]
    else:
        return item.children()


def get_root_children(visible_only: bool) -> list[modo.Item]:
    if visible_only:
        return [
            item
            for item in modo.Scene().items(itype=c.LOCATOR_TYPE, superType=True)
            if item.parent is None and is_visible(item)
        ]
    else:
        return [
            item
            for item in modo.Scene().items(itype=c.LOCATOR_TYPE, superType=True)
            if item.parent is None
        ]


def meshref_transform_to_locator(items: Iterable[modo.Item], tolerance: float):
    matched_transform_groups: dict[Transforms, list[modo.Item]] = dict()
    unprocessed_items = set(items)

    for item in unprocessed_items:
        item_transform = get_transforms(item)
        matched_transform = get_mached_transforms(item_transform, matched_transform_groups, tolerance)

        if matched_transform != item_transform:
            matched_transform_groups.update({matched_transform: [item,]})
        else:
            if matched_transform not in matched_transform_groups:
                matched_transform_groups[matched_transform] = list()
            matched_transform_groups[matched_transform].append(item)

    for matched_items in matched_transform_groups.values():
        first_item = matched_items[0]
        name = f'{first_item.name}{LOCATOR_SUFFIX}'
        transform_loc = modo.Scene().addItem(itype=c.LOCATOR_TYPE, name=name)
        parent_items_to((transform_loc,), first_item, inplace=False)
        parent_items_to((transform_loc,), first_item.parent, get_parent_index(first_item), inplace=True)
        parent_items_to(matched_items, transform_loc, inplace=True)
        for matched_item in matched_items:
            parent_items_to(matched_item.children(), transform_loc, index=1, inplace=True)


def is_transforms_matched(transforms1: Transforms, transfroms2: Transforms, tolerance: float) -> bool:
    return all(v1.equals(v2, tolerance) for v1, v2 in zip(transforms1, transfroms2))


def get_mached_transforms(
        transform: Transforms,
        comparing_transforms: Iterable[Transforms],
        tolerance: float
) -> Transforms:

    for comparing_transform in comparing_transforms:
        if is_transforms_matched(transform, comparing_transform, tolerance):
            return comparing_transform

    return transform


if __name__ == '__main__':
    main()
