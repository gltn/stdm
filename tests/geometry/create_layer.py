line_start = QgsPoint(50,50)
line_end = QgsPoint(100,150)
line = QgsGeometry.fromPolyline([line_start,line_end])

# create a new memory layer
v_layer = QgsVectorLayer("LineString", "line2", "memory")
pr = v_layer.dataProvider()
# create a new feature
seg = QgsFeature()

# add the geometry to the feature, 
seg.setGeometry(QgsGeometry.fromPolyline([line_start, line_end]))
# ...it was here that you can add attributes, after having defined....
# add the geometry to the layer
geom = seg.geometry()
geom.rotate(300, line_end)
pr.addFeatures( [ seg ] )
# update extent of the layer (not necessary)
v_layer.updateExtents()
# show the line  
QgsMapLayerRegistry.instance().addMapLayers([v_layer])