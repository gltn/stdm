/*
 * STDM OpenLayers property overlay definitions
*/
var map, osm, gsat, propertyFeature, propertyLayer, propStyleMap;

var BaseLayerCode = { "GMAPS_SATELLITE": 2010, "OSM": 2011 }

function init() {

    map = new OpenLayers.Map({
        div: "map",
        controls: [
					new OpenLayers.Control.Navigation({
						zoomWheelEnabled: false,						
						'defaultDblClick': function (event) { 
							return; 
						 }
					}),
                    new OpenLayers.Control.Attribution()
                    ],
        projection: new OpenLayers.Projection("EPSG:900913")
    });

    osm = new OpenLayers.Layer.OSM();

    gsat = new OpenLayers.Layer.Google(
                "Google Satellite",
                { type: google.maps.MapTypeId.SATELLITE, numZoomLevels: 22 }
            );
    
    //Contains the property features for overlaying on the basemaps
    propertyLayer = new OpenLayers.Layer.Vector(); 

    map.addLayers([gsat, osm, propertyLayer]);

    map.setCenter(new OpenLayers.LonLat(-72.3, 18.5).transform(
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
 * Zoom to a specific zoom level
*/
function zoom(level) {

    map.zoomTo(level);
	
	return map.getZoom();

}

/*
 * Update the style of the property
*/
function setPropertyStyle(propertyStyle){
	
	var defaultStyle = new OpenLayers.Style(propertyStyle);
	
	propStyleMap = new OpenLayers.StyleMap({
		'default': defaultStyle
	});   
	
	propertyLayer.styleMap = propStyleMap;
	
	propertyLayer.redraw();

}

/*
* Draw the polygon overlay of the property with an optional
* label to use for the polygon.
* 'geometry' - Represents the feature in GeoJSON format.
* OpenLayers has an issue with raw geometry objects in GeoJSON.
*/
function drawProperty(geometry, label) {
    
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

    propertyFeature = geojson_format.read(featObj);

    propertyLayer.addFeatures(propertyFeature);

    if (Array.isArray(propertyFeature)) {
        propertyFeature = propertyFeature[0];
    }

	zoomToPropertyExtent(true);	
	
	return map.getZoom();
    
}

/*
 * Zooms to the extents of the last loaded property.
*/
function zoomToPropertyExtent(doNotReturnLevel){
	
	var bounds = propertyFeature.geometry.getBounds();
	bounds = bounds.scale(1.1);
	map.zoomToExtent(bounds);
	
	if (typeof(doNotReturnLevel) === 'undefined'){	
		
		return map.getZoom();
		
	}

}

/*
 * Removes all overlays in the map
*/
function clearOverlays() {
    if (propertyLayer != null){
        propertyLayer.removeAllFeatures();
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