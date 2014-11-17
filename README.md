STDM Plugin
===========

This is a QGIS plugin that has been implemented using Python and
provides the core GIS functionality for the different STDM modules. By
using QGIS as the host framework for creating and managing geographic
objects, the plugin enables seamleass integration of tenure entities,
for both spatial and textual representations.

Requirements
------------

-   [SQLAlchemy][] 0.8 or higher
-   [GeoAlchemy][] 2
-   [reportlab][]
-   [fontTools][]
-   [ttfquery][]
-   [XML to DDL][]

  [SQLAlchemy]: https://pypi.python.org/pypi/SQLAlchemy
  [GeoAlchemy]: https://github.com/geoalchemy/geoalchemy2
  [reportlab]: https://pypi.python.org/pypi/reportlab
  [fontTools]: https://pypi.python.org/pypi/FontTools
  [ttfquery]: https://pypi.python.org/pypi/TTFQuery
  [XML to DDL]: http://xml2ddl.berlios.de/

  The third party python libraries required to support this plugin are
  bundled together in the third_party folder inside the STDM plugin folder.
