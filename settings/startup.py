

import qgis.utils
if u'stdm' not in qgis.utils.active_plugins:
    status = qgis.utils.loadPlugin(u'stdm')
    if status:
        qgis.utils.startPlugin(u'stdm')
