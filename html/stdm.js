/*
 * STDM OpenLayers spatial unit overlay.
*/
var map, osm, gsat, spatialUnitFeature, spatialUnitLayer, spUnitStyleMap;

var BaseLayerCode = { "GMAPS_SATELLITE": 2010, "OSM": 2011 }

function init() {

    map = new OpenLayers.Map({
        div: "map",
        controls: [
					new OpenLayers.Control.Navigation({
						zoomWheelEnabled: true,
						'defaultDblClick': function (event) { 
							return; 
						 }
					}),
                    new OpenLayers.Control.Attribution()
                    ],
        projection: new OpenLayers.Projection("EPSG:900913"),
        eventListeners:{
                "moveend": mapEvent,
                "zoomend": mapEvent
        }
    });

    osm = new OpenLayers.Layer.OSM();

    gsat = new OpenLayers.Layer.Google(
                "Google Satellite",
                { type: google.maps.MapTypeId.SATELLITE, numZoomLevels: 24 }
            );
    
    //Contains the property features for overlaying on the basemaps
    spatialUnitLayer = new OpenLayers.Layer.Vector();

    map.addLayers([gsat, osm, spatialUnitLayer]);

    //TODO: Remove hardcode of map center

    map.setCenter(new OpenLayers.LonLat(-74.184392,4.564353).transform(
                        new OpenLayers.Projection("EPSG:4326"),
                        map.getProjectionObject()
                    ), 5);

}

/*
 * Set the centre of the map at the specified zoom level
*/
function setCenter(x, y, zoom) {

    map.setCenter([x, y], zoom);

}

/*
 * Raised on 'moveend' and 'zoomend' events.
 */
function mapEvent(event){
    zoom_level = map.getZoom();
    sp_loader.onZoomLevelChanged(zoom_level);
}

/*
 * Zoom to a specific zoom level
*/
function zoom(level) {

    map.zoomTo(level);
	
	return map.getZoom();

}

/*
 * Update the style of the spatial unit.
*/
function setSpatialUnitStyle(spUnitStyle){
	
	var defaultStyle = new OpenLayers.Style(spUnitStyle);
	
	spUnitStyleMap = new OpenLayers.StyleMap({
		'default': defaultStyle
	});   
	
	spatialUnitLayer.styleMap = spUnitStyleMap;
	
	spatialUnitLayer.redraw();

}

/*
* Draw the point/line/polygon overlay of the spatial unit with an optional
* label to use for the spatial unit.
* 'geometry' - Represents the feature in GeoJSON format.
* OpenLayers has an issue with raw geometry objects in GeoJSON.
*/
function drawSpatialUnit(geometry, label) {
    
    clearOverlays();

    //Format input string to a compatible GeoJSON format
    var geomObj = JSON.parse(geometry);

    var featObj = new Object();
    featObj["type"] = "Feature";
    featObj["geometry"] = geomObj;

	if (label){
		featObj["properties"] = label;
	}

    var geojson_format = new OpenLayers.Format.GeoJSON();

    spatialUnitFeature = geojson_format.read(featObj);

    spatialUnitLayer.addFeatures(spatialUnitFeature);

    if (Array.isArray(spatialUnitFeature)) {
        spatialUnitFeature = spatialUnitFeature[0];
    }

	zoomToSpatialUnitExtent(true);
	
	return map.getZoom();
    
}

/*
 * Zooms to the extents of the last loaded spatial unit.
*/
function zoomToSpatialUnitExtent(doNotReturnLevel){
    if (spatialUnitFeature) {

        var bounds = spatialUnitFeature.geometry.getBounds();
        bounds = bounds.scale(1.2);
        map.zoomToExtent(bounds);

        if (typeof(doNotReturnLevel) === 'undefined') {

            return map.getZoom();

        }
    }
}

/*
 * Removes all overlays in the map
*/
function clearOverlays() {
    if (spatialUnitLayer != null){
        spatialUnitLayer.removeAllFeatures();
    }
}

/*
 * Change the map's baselayer. The STDM Python enumerations have been used to identify
 * the codes.
*/
function setBaseLayer(code) {

    if (code == BaseLayerCode.GMAPS_SATELLITE) {
        map.setBaseLayer(gsat);
    }

    else if (code == BaseLayerCode.OSM) {
        map.setBaseLayer(osm);
    }
	
	return map.getZoom();

}
/*
 * Zoom the map extents to the given map bounds specified as an array.
 */
function zoomToExtents(extents){
    bounds = new OpenLayers.Bounds(extents);
    bounds.transform(new OpenLayers.Projection("EPSG:4326"),
                        map.getProjectionObject());

    map.zoomToExtent(bounds);
}