"""
/***************************************************************************
Name                 : STDM User
Description          : Generic STDM User Class
Date                 : 25/May/2013 
copyright            : (C) 2013 by John Gitau
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
class User(object):
    """
    Container for basic user account settings.
    'Validity' is of PyDate type
    """
    def __init__(self,UserName,Password='',Validity = None,Approved = True):
        self.UserName = UserName
        self.Password = Password
        self.Approved = Approved
        self.Validity = Validity