"""
/***************************************************************************
Name                 : ReverseDict
Description          : A dictionary which can lookup values by key, and keys
                       by value. All values and keys must be hashable, and
                       unique.
Date                 : 8/April/2014
copyright            : (C) 2014 by John Gitau
email                : gkahiu@gmail.com
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


class ReverseDict(dict):
    '''
    A dictionary which can lookup values by key, and keys by value.
    All values and keys must be hashable, and unique.
    '''

    def __init__(self, *args, **kw):
        dict.__init__(self, *args, **kw)
        self.reverse = dict((reversed(list(i)) for i in list(self.items())))

    def __setitem__(self, key, value):
        dict.__setitem__(self, key, value)
        self.reverse[value] = key
