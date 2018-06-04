
var map
var infoWindow
var currentLocation = null;
var mapMarkers = [];



function initMap() {
    map = new google.maps.Map(document.getElementById('entryLocationMap'), {
      center: {lat: -34.397, lng: 150.644},
      zoom: 6

    });
    infoWindow = new google.maps.InfoWindow;

	// This event listener calls addMarker() when the map is clicked.
	google.maps.event.addListener(map, 'click', function(event) {
		addMarker(event.latLng, map);
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

    // Try HTML5 geolocation.
    if (navigator.geolocation) {
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
    }
}

function handleLocationError(browserHasGeolocation, infoWindow, pos) {
	infoWindow.setPosition(pos);
	infoWindow.setContent(browserHasGeolocation ?
                      'Error: The Geolocation service failed.' :
                      'Error: Your browser doesn\'t support geolocation.');
	infoWindow.open(map);
}




$(function () {

		var dropZone = document.getElementById('drop-zone');
		var uploadForm = document.getElementById('js-upload-form');
		var imageUUID = null;
		var tmpFileName = null;
		var currentStep = 1;
		var lastStep = 5;



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
				if	($("#formField_title").val().length >= 3){
					if ($("#formField_description").val().length >= 5){
						valid = true;
					}
				}
			}else if (currentStep == 4){
				valid = true;

			}else if (currentStep == 5){
				//valid = true;
			}else if (currentStep == 6){
				valid = true;
			}

			if (valid == true){
				$('#next-step').prop('disabled', false);
				$('#next-step').css("display", "Block");
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
						dataSet = {'title':title, 'description':description, 'categoryID':catID, 'UUID':UUID , 'tmpFileName':tmpFileName}
						
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
					populateCategories()
					transitionNextStep()
					setupImagePreview(data.TMPFileName)
				},
			});
		}
});
