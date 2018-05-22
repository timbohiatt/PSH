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
				//$(element).fadeOut("fast")
				$(element).css("display", "None")
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
    		setTimeout(function(){
				element = ("#step-" + currentStep)
				//$(element).fadeOut("fast")
				$(element).css("display", "None")
				setTimeout(function(){
					currentStep = currentStep - 1
					validateButtons()
					validateEntryData()
					element = ("#step-" + currentStep)
					//$(element).fadeIn("fast")
					$(element).css("display", "Block")
				}, 100);
			}, 100);
    	}

		function validateButtons(){
			if (currentStep == 1){
				$("#previous-step-holder").css("display", "None");
				$("#next-step-holder").css("display", "None");
				$("#upload-preview").css("display", "None");
				$("#submit-step-holder").css("display", "None");
			}else if(currentStep == lastStep){
				$("#previous-step-holder").css("display", "None");
				$("#next-step-holder").css("display", "None");
				$("#submit-step-holder").css("display", "Block");
			}
			else{
				$("#previous-step-holder").css("display", "Block");
				$("#next-step-holder").css("display", "Block");
				$("#submit-step-holder").css("display", "None");
			}

		}

		function formReset(){
			setTimeout(function(){
               $("#submit-step-1").fadeIn("slow")
            }, 100);
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
				console.log("Validating Step 2")
				console.log($("#form_CatSelect option:selected").val())
				if ($("#form_CatSelect option:selected").val() != 999){	
					console.log("Step 2 Valid")
					valid = true;
				}	
			}else if (currentStep == 3){
				console.log("Validating Step 3")
				if	($("#formField_title").val().length >= 3){
					if ($("#formField_description").val().length >= 5){
						valid = true;
					}
				}
			}else if (currentStep == 4){
				console.log("Validating Step 4")
				valid = true;

			}else if (currentStep == 5){
				console.log("Validating Step 5")
				valid = true;
			}else if (currentStep == 6){
				console.log("Validating Step 6")
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


		$('#form_CatSelect').change(function() {
        	populateCategoryRules()
    	});

		

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

			$("#uploadTextPlaceholder").css("display", "None");
			$("#uploadProcessing").attr("src",("/static/img/processing.gif"))
			$("#uploadProcessing").css("display", "block");
			
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
		//-------------------------------------------



		function submitEntry(){
			setTimeout(function(){
				$("#upload-preview").fadeOut("slow")
				setTimeout(function(){
					$(element).fadeOut("slow")
					setTimeout(function(){
						$("#step-processing").fadeIn("slow")
						title = $("#formField_title").val()
						description = $("#formField_description").val()
						catID = $("#form_CatSelect").val()
						UUID = imageUUID
						console.log(UUID, tmpFileName)
						dataSet = {'title':title, 'description':description, 'categoryID':catID, 'UUID':UUID , 'tmpFileName':tmpFileName}
						console.log(JSON.stringify(dataSet))
						
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
				$("#step-processing").fadeOut("slow")
				setTimeout(function(){
					$("#step-completed").fadeIn("slow")
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
					console.log(data)
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
