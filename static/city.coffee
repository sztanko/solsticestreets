###
 * New coffeescript file
###
attr = 'Map data &copy; <a href="http://openstreetmap.org">OpenStreetMap</a> contributors, Imagery © <a href="http://mapbox.com">MapBox</a>'
console.log city
center = 
    lat: (+city.top + +city.bottom)/2
    lng: (+city.left + +city.right)/2
console.log center
console.log stats
map = L.map('map').setView(center, 12);
#http://{s}.tile.cloudmade.com/fe623ce312234f8f9333bbee72d4a176/64657/256/{z}/{x}/{y}.png',

L.tileLayer('https://a.tiles.mapbox.com/v3/sztanko.gjp73mna/{z}/{x}/{y}.png', {
    attribution: attr,
    maxZoom: 18
}).addTo(map);


colorscale = d3.scale.linear().domain([0,3]).range(["orange", "#0000AA"]).interpolate(d3.interpolateHcl)

legend = L.control({position: 'bottomleft'});
legend.onAdd = (map) ->
	this._div = L.DomUtil.get("legendContent")
	return this._div
	
legend.addTo(map);

clegend = L.control({position: 'topright'});
clegend.onAdd = (map) ->
	this._div = L.DomUtil.get("legendColours")
	return this._div
	
clegend.addTo(map);


geoJson = {}

winterStyle = (f) ->
	return {
    "color": "red",
    weight: 4
	}

summerStyle = (f) ->
	return {
    "color": "orange",
    weight: 4
	}
	
pieGen = (s, radius) ->
	deg2xy = (deg, r) ->
		rad = deg / 180*Math.PI
		xy = [Math.round(r * Math.sin(rad)),  - Math.round(r * Math.cos(rad)) ]
		return xy
		
	#pHist = [i for i in s.hist][0]
	pHist = s.hist
	#console.log pHist
	maxN = _.max(pHist)
	r = radius/maxN
	c1 = _.map(pHist, (d, i) ->
		xy = deg2xy(i, r*d)
		xy1 = deg2xy(i+1, r*d)
		p = "L"+xy[0]+" "+xy[1] + "L"+xy1[0]+" "+xy1[1]
	)
	c2 = _.map(pHist, (d, i) ->
		xy = deg2xy(i, -r*d)
		xy1 = deg2xy(i+1, -r*d)
		p = "L"+xy[0]+" "+xy[1] + "L"+xy1[0]+" "+xy1[1]
	)
	path = "M0 0 "+c1.join(" ")+c2.join(" ")+" L0 0"

	winterSunPath = "M"+deg2xy(s.sun_azimuth, -radius)+" L"+deg2xy(s.sun_azimuth, radius)
	summerSunPath = "M"+deg2xy(s.summer_sun_azimuth, -radius)+" L"+deg2xy(s.summer_sun_azimuth, radius)
	
	ticks = _.chain(_.range(0,360,5)).map((i) -> "M"+deg2xy(i,0)+"L"+deg2xy(i,200)).value().join(" ")

	#console.log(path)
	#console.log(maxN)
	return [path, winterSunPath, summerSunPath, ticks]
	
pathes = pieGen(stats,180)
$("#pie").attr("d", pathes[0])
$("#winterSun").attr("d", pathes[1])
$("#summerSun").attr("d", pathes[2])
$("#ticks").attr("d", pathes[3])

popup = (feature, layer) -> 
	if feature.properties.name!=null
		layer.bindPopup(feature.properties.name+"<br>\n "+feature.properties.azimuth_d+"° difference from the sun path")
	else
		layer.bindPopup(feature.properties.azimuth_d+"° difference from the sun path")

summerSegments = L.geoJson(summer, {
	style: summerStyle,
	onEachFeature: popup
	}).addTo(map);
winterSegments = L.geoJson(winter, {
	style: winterStyle,
	onEachFeature: popup
	}).addTo(map);

