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
from PyQt4.QtCore import QSettings, QT_VERSION
from PyQt4.QtNetwork import QNetworkProxy


def get_proxy():

    # Adaption by source of "Plugin Installer - Version 1.0.10"
    """
    :rtype : QNetworkProxy
    :return: Proxy
    """
    proxy = None
    settings = QSettings()
    settings.beginGroup("proxy")

    # Check if the 'proxy' group exists
    proxy_keys = settings.childKeys()
    if len(proxy_keys) == 0:
        return

    if settings.value("/proxyEnabled", type=bool):
        proxy = QNetworkProxy()
        proxy_type = settings.value("/proxyType", "")
        # if len(args)>0 and settings.value("/proxyExcludedUrls").toString()
        # .contains(args[0]):
        # proxyType = "NoProxy"
        if proxy_type in ["1", "Socks5Proxy"]:
            proxy.setType(QNetworkProxy.Socks5Proxy)
        elif proxy_type in ["2", "NoProxy"]:
            proxy.setType(QNetworkProxy.NoProxy)
        elif proxy_type in ["3", "HttpProxy"]:
            proxy.setType(QNetworkProxy.HttpProxy)
        elif proxy_type in ["4", "HttpCachingProxy"] and QT_VERSION >= 0X040400:
            proxy.setType(QNetworkProxy.HttpCachingProxy)
        elif proxy_type in ["5", "FtpCachingProxy"] and QT_VERSION >= 0X040400:
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
