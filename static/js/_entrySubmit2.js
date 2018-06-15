




//====================================================================================================
// FORM RELATED FUNCTIONS
//====================================================================================================

//$(function () {

		var dropZone = document.getElementById('drop-zone');
		var uploadForm = document.getElementById('js-upload-form');
		var imageUUID = null;
		var tmpFileName = null;
		var currentStep = 1;
		var lastStep = 5;
		var imageLabels = [];
		var entryLocation = {};
		var categoryData = null;

		$('#previous-step').click(function() {
			transitionPreviousStep()
    	});

		$('#next-step').click(function() {
			$("#step-p").css("display", "block");
			transitionNextStep()
			$('#next-step').css("display", "Block");
			$('#next-step').prop('disabled', true);
    	});

		$('#submit-step').click(function() {
			submitEntry()
    	});

    	
    	function transitionNextStep(){
    		setTimeout(function(){
				element = ("#step-" + currentStep)
				$(element).fadeOut("fast")
				$(element).css("display", "None")
				$("#step-p").css("display", "none");
				setTimeout(function(){
					currentStep = currentStep + 1
					validateButtons()
					validateEntryData()
					element = ("#step-" + currentStep)
					$(element).css("display", "Block")
					//$(element).fadeIn("fast")
				}, 100);
			}, 100);
    	}
    	function transitionPreviousStep(){
    		element = ("#step-" + currentStep)
    		$(element).css("display", "None")
    		currentStep = (currentStep - 1)
    		validateButtons()
			validateEntryData()
			element = ("#step-" + currentStep)
			$(element).css("display", "Block")
    	}

		function validateButtons(){
			if (currentStep == 1){
				$("#previous-step").css("display", "None");
				$("#next-step").css("display", "None");
				$("#upload-preview").css("display", "None");
				$("#submit-step").css("display", "None");
			}else if(currentStep == lastStep){
				$("#previous-step").css("display", "Block");
				$("#next-step").css("display", "None");
				$("#submit-step").css("display", "Block");
			}
			else{
				$("#previous-step").css("display", "Block");
				$("#next-step").css("display", "Block");
				$("#submit-step").css("display", "None");
			}

		}

		$("#form_CatSelect").change(function() {
			$("#category-detail-description-title").css("display", "Block");
			$("#category-detail-title").html(categoryData[($(this).prop('selectedIndex')-1)][4])
			$("#category-detail-description").html(categoryData[($(this).prop('selectedIndex')-1)][2])
		  	validateEntryData()
		});
		$("#formField_title").keyup(function() {
		  	validateEntryData()
		});
		$("#formField_description").keyup(function() {
		  	validateEntryData()
		});



		function validateEntryData(){
			valid = false

			if (currentStep == 2){
				if ($("#form_CatSelect option:selected").val() != 999){	
					valid = true;
				}	
			}else if (currentStep == 3){
				if	($("#formField_title").val().length >= 8){
					
					$("#validation-text-title").removeClass();
			        $("#validation-text-title").css({fontSize: 12});
			        $("#validation-text-title").addClass("text-success");
			        $('#validation-text-title').html("Good Title!")

					if ($("#formField_description").val().length >= 15){

						$("#validation-text-description").removeClass();
			        	$("#validation-text-description").css({fontSize: 12});
			        	$("#validation-text-description").addClass("text-success");
			        	$('#validation-text-description').html("Good Description!")


						valid = true;
					}else{
						$("#validation-text-description").removeClass();
			        	$("#validation-text-description").css({fontSize: 12});
			        	$("#validation-text-description").addClass("text-danger");
			        	$('#validation-text-description').html("Provide a description for your entry. Tell us about it or how you got your shot.")

					}
				}else{
			        $("#validation-text-title").removeClass();
			        $("#validation-text-title").css({fontSize: 12});
			        $("#validation-text-title").addClass("text-danger");
			        $('#validation-text-title').html("Provide a good title for your entry.")
				}
			}else if (currentStep == 4){
				if( ($.trim( $('#place-name').html() ).length) >= 1 ) {
					if( ($.trim( $('#place-address').html() ).length) >= 1 ) {
						valid = true;
					}
				}
			}else if (currentStep == 5){
				valid = true;
				
			}else if (currentStep == 6){
				valid = true;
			}

			if (valid == true){
				if (currentStep != lastStep){
					$('#next-step').prop('disabled', false);
					$('#next-step').css("display", "Block");
				}
			}else{
				$('#next-step').prop('disabled', true);
				$('#next-step').css("display", "None");
			}
		}


		function setupImagePreview(TMPFileName){
			$("#upload-preview").attr("src",("/static/media/MPSH_entries/stage/"+TMPFileName))
			//$("#upload-preview2").attr("src",("/static/media/MPSH_entries/stage/"+TMPFileName))

			$("#upload-preview").css("display", "block");
			//$("#upload-preview2").css("display", "block");
		}


		//--------- Drop Zone Configuration ---------
		//-------------------------------------------
		dropZone.ondrop = function(e) {
			e.preventDefault();
			this.className = 'upload-drop-zone';

			$("#step-1").css("display", "None");
			$("#uploadProcessing").attr("src",("/static/img/processing.gif"))
			$("#step-p").css("display", "block");
			
			uploadPhoto(e.dataTransfer.files)
		}

		dropZone.ondragover = function() {
			this.className = 'upload-drop-zone drop';
			return false;
		}

		dropZone.ondragleave = function() {
			this.className = 'upload-drop-zone';
			return false;
		}


		$("#uploadTextPlaceholder_Click").change(function() {
			$("#step-1").css("display", "None");
			$("#uploadProcessing").attr("src",("/static/img/processing.gif"))
			$("#step-p").css("display", "block");
			uploadPhoto($("#uploadTextPlaceholder_Click").prop('files'))
    	});

		//-------------------------------------------

		function submitEntry(){
			setTimeout(function(){
				 element = ("#step-" + currentStep)
				$(element).fadeOut("fast")
				$("#next-step").fadeOut("fast")
				$("#previous-step").fadeOut("fast")
				$("#submit-step").fadeOut("fast")
				$("#upload-preview").fadeOut("fast")
				$(element).css("display", "None")
				$("#step-p").css("display", "Block");
				
				setTimeout(function(){
					$(element).fadeOut("slow")
					setTimeout(function(){
						$("#step-p").fadeIn("slow")
						title = $("#formField_title").val()
						description = $("#formField_description").val()
						catID = $("#form_CatSelect").val()
						UUID = imageUUID
						dataSet = {'title':title, 'description':description, 'categoryID':catID, 'UUID':UUID , 'tmpFileName':tmpFileName, 'imageLabels': imageLabels, 'entryLocation': entryLocation}
						
						$.ajax({
							type: 'POST',
							url: '/api/v1.0/entry/submit',
							data: JSON.stringify(dataSet),
							contentType: false,
							cache: false,
							processData: false,
							async: true,
							success: function(data) {
								processResult(data["statusCode"], data["status"], data["statusLongText"])
							},
						});

					}, 1000);
				}, 1000);
			}, 1000);
		}


		function processResult(statusCode, status, statusLongText){
			$("#result-status").text(status);
			$("#result-statusText").text(statusLongText);
			setTimeout(function(){
				$("#step-p").fadeOut("slow")
				setTimeout(function(){
					$("#step-f").fadeIn("slow")
				}, 1000);
			}, 1000);
		}

		function populateLabels(data){
			data = data["labels"] 
			imageLabels = []
			for (index = 0; index < data.length; ++index) {
				label = data[index]["Description"].replace(/\s/g,'')

				imageLabels.push(label);
			}

			
		}


		function populateCategories(){

			$.ajax({
				type: 'POST',
				url: '/api/v1.0/entry/outstandingCategories',
				//data: form_data,
				contentType: false,
				cache: false,
				processData: false,
				async: true,
				success: function(data) {
					data = JSON.parse(data)
					categoryData = data
					$("#form_CatSelect").append("<option value='"+999+"'>Select Photo Category</option>");
					for (index = 0; index < data.length; ++index) {
    					$("#form_CatSelect").append("<option value='"+data[index][0]+"'>"+data[index][1]+"</option>");
					}
					$("#form_CatSelect").val('999');
					populateCategoryRules()
				},
			});
		}


		function populateCategoryRules(){

			catID = $("#form_CatSelect").val()
			dataSet = {'categoryID':catID}

			$.ajax({
				type: 'POST',
				url: '/api/v1.0/category/categoryGuide',
				data: JSON.stringify(dataSet) ,
				contentType: false,
				cache: false,
				processData: false,
				async: true,
				success: function(data) {
					data = JSON.parse(data)
				},
			});
		}


		function uploadPhoto(file){
			var form_data = new FormData()
			form_data.append('file', file[0])

			$.ajax({
				type: 'POST',
				url: '/api/v1.0/photo/upload',
				data: form_data,
				contentType: false,
				cache: false,
				processData: false,
				async: true,
				success: function(data) {
					data = JSON.parse(data)
					imageUUID = data.UUID
					tmpFileName = data.TMPFileName
					populateLabels(data.Vision[0])
					populateCategories()
					transitionNextStep()
					setupImagePreview(data.TMPFileName)
				},
			});
		}
//});




//====================================================================================================
//====================================================================================================
//	MAP RELATED FUNCTIONS
//====================================================================================================

var map
var infoWindow
var currentLocation = null;
var mapMarkers = [];
var autocomplete;
var infowindowContent;
var infowindow;
var geocoder;

function initMap() {
	
    infowindow = new google.maps.InfoWindow();
    infowindow.setContent(infowindowContent);
	infowindowContent = document.getElementById('infowindow-content');
	input = document.getElementById('formField_locationSearch');
	autocomplete = new google.maps.places.Autocomplete(input)
	infoWindow = new google.maps.InfoWindow;
	geocoder = new google.maps.Geocoder;
    map = new google.maps.Map(document.getElementById('entryLocationMap'), {
      center: {lat: -34.397, lng: 150.644},
      zoom: 1,
      zoomControl: false,
	  mapTypeControl: false,
	  scaleControl: false,
	  streetViewControl: false,
	  rotateControl: false,
	  fullscreenControl: false

    });

    var marker = new google.maps.Marker({
          map: map,
          anchorPoint: new google.maps.Point(0, -29)
        });

	// Adds a marker to the map.
	function addMarker(location, map) {
	// Add the marker at the clicked location, and add the next-available label
	// from the array of alphabetical characters.

		for (var i = 0; i < mapMarkers.length; i++) {
		    mapMarkers[i].setMap(null);
		}
		var marker = new google.maps.Marker({
			position: location,
			//label: labels[labelIndex++ % labels.length],
			map: map
		});
		mapMarkers.push(marker);
		map.panTo(marker.getPosition())
	}


	autocomplete.addListener('place_changed', function() {
		  clearLocationData()
          infowindow.close();
          marker.setVisible(false);
          var place = autocomplete.getPlace();
          if (!place.geometry) {
            // User entered the name of a Place that was not suggested and
            // pressed the Enter key, or the Place Details request failed.
          	validateEntryData()
            return;
          }

          // If the place has a geometry, then present it on a map.
          if (place.geometry.viewport) {
            map.fitBounds(place.geometry.viewport);
          } else {
            map.setCenter(place.geometry.location);
            map.setZoom(17);  // Why 17? Because it looks good.
          }
          addMarker(place.geometry.location, map)
          //marker.setPosition(place.geometry.location);
          marker.setVisible(true);

          var address = '';
          if (place.address_components) {
            address = [
              (place.address_components[0] && place.address_components[0].short_name || ''),
              (place.address_components[1] && place.address_components[1].short_name || ''),
              (place.address_components[2] && place.address_components[2].short_name || '')
            ].join(' ');
          }

          //infowindowContent.children['place-icon'].src = place.icon;
          setLocationData(place, address)
          //infowindowContent.children['place-name'].textContent = place.name;
          //infowindowContent.children['place-address'].textContent = address;
          infowindow.open(map, marker);
          validateEntryData()
    });



	// This event listener calls addMarker() when the map is clicked.
	google.maps.event.addListener(map, 'click', function(event) {
		clearLocationData()
		//geocodeLatLng(geocoder, map, infowindow);
		validateEntryData()
	});

    // Try HTML5 geolocation.
    /*if (navigator.geolocation) {
      navigator.geolocation.getCurrentPosition(function(position) {
        var pos = {
          lat: position.coords.latitude,
          lng: position.coords.longitude
        };

        infoWindow.setPosition(pos);
        //infoWindow.setContent('Location found.');
        //infoWindow.open(map);
        map.setCenter(pos);
      }, function() {
        handleLocationError(true, infoWindow, map.getCenter());
      });
    } else {
      // Browser doesn't support Geolocation
      handleLocationError(false, infoWindow, map.getCenter());
    }*/


}


function geocodeLatLng(geocoder, map, infowindow) {


        //var input = document.getElementById('latlng').value;
        //var latlngStr = input.split(',', 2);
        //var latlng = {lat: parseFloat(latlngStr[0]), lng: parseFloat(latlngStr[1])};
        geocoder.geocode({'location': latlng}, function(results, status) {
          if (status === 'OK') {
            if (results[0]) {
              map.setZoom(11);
              addMarker(event.latLng, map);
              //var marker = new google.maps.Marker({
              //  position: latlng,
              //  map: map
              //});
              //infowindow.setContent(results[0].formatted_address);
              setLocationData(place, results[0].formatted_address)
           	  //infowindowContent.children['place-name'].textContent = "Dropped Pinn";
              //infowindowContent.children['place-address'].textContent = results[0].formatted_address;
              //infowindow.open(map, marker);
            } else {
              window.alert('No results found');
            }
          } else {
            window.alert('Geocoder failed due to: ' + status);
          }

        });
      }



function setLocationData(place, address){
          //infowindowContent.children['place-icon'].src = null
		  infowindowContent.children['place-name'].textContent = place.name;
          infowindowContent.children['place-address'].textContent = address;

          entryLocation["place-address"] = address;
          entryLocation["place-name"] = place.name;
          entryLocation["place-id"] = place.place_id;


}


function clearLocationData(){
          //infowindowContent.children['place-icon'].src = null
          infowindowContent.children['place-name'].textContent = null;
          infowindowContent.children['place-address'].textContent = null;
}

//Map Event Handler
function handleLocationError(browserHasGeolocation, infoWindow, pos) {
	infoWindow.setPosition(pos);
	infoWindow.setContent(browserHasGeolocation ?
                      'Error: The Geolocation service failed.' :
                      'Error: Your browser doesn\'t support geolocation.');
	infoWindow.open(map);
}



//====================================================================================================
// END MAP RELATED FUNCTIONS
//====================================================================================================

