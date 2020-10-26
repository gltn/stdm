# -*- coding: utf-8 -*-
"""
/***************************************************************************
    Useful network functions
                             -------------------
    begin            : 2011-03-01
    copyright        : (C) 2011 by Luiz Motta
    author           : Luiz P. Motta
    email            : motta _dot_ luiz _at_ gmail.com
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
from qgis.PyQt.QtCore import QSettings
from qgis.PyQt.QtNetwork import QNetworkProxy


def getProxy():

    # Adaption by source of "Plugin Installer - Version 1.0.10"
    proxy = None
    settings = QSettings()
    settings.beginGroup("proxy")

    #Check if the 'proxy' group exists
    proxyKeys = settings.childKeys()
    if len(proxyKeys) == 0:
        return

    if settings.value("/proxyEnabled",type=bool):
        proxy = QNetworkProxy()
        proxyType = settings.value("/proxyType","")
        #if len(args)>0 and settings.value("/proxyExcludedUrls").toString().contains(args[0]):
        #  proxyType = "NoProxy"
        if proxyType in ["1","Socks5Proxy"]:
            proxy.setType(QNetworkProxy.Socks5Proxy)
        elif proxyType in ["2","NoProxy"]:
            proxy.setType(QNetworkProxy.NoProxy)
        elif proxyType in ["3","HttpProxy"]:
            proxy.setType(QNetworkProxy.HttpProxy)
        elif proxyType in ["4","HttpCachingProxy"]:
            proxy.setType(QNetworkProxy.HttpCachingProxy)
        elif proxyType in ["5","FtpCachingProxy"]:
            proxy.setType(QNetworkProxy.FtpCachingProxy)
        else:
            proxy.setType(QNetworkProxy.DefaultProxy)
            proxy.setHostName(settings.value("/proxyHost"))
            port = settings.value("/proxyPort")
            if port != "":
                proxy.setPort(int(port))
            proxy.setUser(settings.value("/proxyUser"))
            proxy.setPassword(settings.value("/proxyPassword"))

    settings.endGroup()
    return proxy