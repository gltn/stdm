"""
/***************************************************************************
Name                 : RenameableKeyDict
Description          : OrderedDict which enables renaming of keys.
Date                 : 17/July/2017
copyright            : (C) 2017 by UN-Habitat and implementing partners.
                       See the accompanying file CONTRIBUTORS.txt in the root
email                : stdm@unhabitat.org
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""

from collections import MutableMapping


class RenameableKeyDict(MutableMapping):
    """
    An ordered dictionary which enables the renaming of keys and optionally
    replacing their values while still retaining their position in the
    collection.
    """
    def __init__(self, *args, **kwds):
        """
        Initializes the dictionary. The signature is the same as
        regular dictionaries, but keyword arguments are not recommended
        because their insertion order is arbitrary.
        """
        self._values = []
        self._idx_map = {}

        self.update(*args, **kwds)

    def __getitem__(self, key):
        if key not in self._idx_map:
            raise KeyError(str(key))

        idx = self._get_idx(key)

        return self._values[idx]

    def _get_idx(self, key):
        # Get the position of the value in the list
        idx = self._idx_map[key]
        if idx >= len(self._values):
            raise IndexError(str(key))

        return idx

    def __setitem__(self, key, value):
        if key in self._idx_map:
            idx = self._get_idx(key)
            prv_item = self._values.pop(idx)

            # Insert at the same position
            self._values.insert(idx, value)

            del prv_item

        else:
            # Item will be inserted at the end
            insert_idx = len(self._values)
            self._values.append(value)

            # Update reference map
            self._idx_map[key] = insert_idx

    def __len__(self):
        return len(self._values)

    def __delitem__(self, key):
        if key not in self._idx_map:
            raise KeyError(str(key))

        idx = self._get_idx(key)

        # Remove reference from map
        del self._idx_map[key]

        rem_item = self._values.pop(idx)
        del rem_item

    def _sorted_keys(self):
        # Returns keys in the index map sorted by index value in
        # ascending order
        return map(
            lambda s: s[0],
            sorted(self._idx_map.items(), key=lambda c:c[1])
            )

    def __iter__(self):
        keys = self._sorted_keys()
        idx = 0
        while idx < len(keys):
            yield keys[idx]
            idx += 1

    def __contains__(self, key):
        return key in self._idx_map

    def clear(self):
        self._idx_map.clear()
        self._values = []

    def rename(self, old, new, item=None):
        """
        Rename a key with a new value while still retaining the position of 
        the value. Optionally, the value could also be replaced.
        :param old: Old key whose value is to be replaced.
        :type old: str
        :param new: New key which replaces the existing one.
        :type new: str
        :param item: An optional value to replace the existing value 
        for the given key.
        :type item: None
        """
        if old not in self._idx_map:
            raise KeyError(str(old))

        idx = self._get_idx(old)
        del self._idx_map[old]

        # Insert renamed key using the list index as the value
        self._idx_map[new] = idx

        # Update item if specified
        if not item is None:
            old_item = self._values.pop(idx)
            self._values.insert(idx, item)

            del old_item