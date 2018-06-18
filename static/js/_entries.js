
//====================================================================================================
//====================================================================================================
//	MAP RELATED FUNCTIONS
//====================================================================================================
var mapMarkers = []
var marker = null
var map = null

function initMap() {

 console.log(appConfig.entries)
 console.log(JSON.parse(appConfig.entries))
 console.log(typeof(appConfig.entries))
 
  // The location of Uluru
  var uluru = {lat: -25.344, lng: 131.036};

  map = new google.maps.Map(document.getElementById('entryLocationMap'), {
    zoom: 4,
    center: uluru
  });

   x =  JSON.parse(appConfig.entries)

  for (var entry in x )
  {
  	console.log(entry)
  	var marker = new google.maps.Marker({
	  position: {lat: entry.location.latitude, lng: entry.location.longitude},
	  map: maps
  	});
  }

}



//====================================================================================================
// END MAP RELATED FUNCTIONS
//====================================================================================================

