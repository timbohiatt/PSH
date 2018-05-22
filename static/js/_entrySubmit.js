$(function () {


		function loadVsionData(json){
			visionLabels = json[0].labels
			var table = document.getElementById("upload-preview-vision-data");
			
			while (table.firstChild) {
			    table.removeChild(table.firstChild);
			}

			var row = document.createElement("tr");
			var cell = document.createElement("td");
			var cellText = document.createTextNode("Detected Item");
		    cell.appendChild(cellText);
		    row.appendChild(cell);

			var cell = document.createElement("td");
			var cellText = document.createTextNode("% Chance");
		    cell.appendChild(cellText);
		    row.appendChild(cell);

		    table.appendChild(row);

			var cell = document.createElement("td");

			for(var i = 0; i < visionLabels.length; i++) {
				
				var item = visionLabels[i];

				if (item["Upload_Display"] == "True"){
					

					var row = document.createElement("tr");
					
					var cell = document.createElement("td");
      				var cellText = document.createTextNode(item["Description"]);
				    cell.appendChild(cellText);
				    row.appendChild(cell);
				    
				    var cell = document.createElement("td");
      				var cellText = document.createTextNode(item["Score_Dec"]+"%");
      				cell.appendChild(cellText);
      				row.appendChild(cell);
      				
      				table.appendChild(row);

      			}

      		}
	
      			/*
    			if (item["Upload_Display"] == "True"){
	    			li.appendChild(document.createTextNode(i +" - "+item["Description"] + " " + item["Score_Dec"] + "% " + item["Upload_Display"]));
					li.setAttribute("id", ("Vision-Label-"+i)); 
					ul.appendChild(li);
				}
    			if (item["Upload_Display"] == "True"){
					li.appendChild(document.createTextNode(i +" - "+item["Description"] + " " + item["Score"] + " " + item[""]));
					li.setAttribute("id", ("Vision-Label-"+i)); 
					ul.appendChild(li);
    			}*/

			
			table.appendChild(row);
		}

	    $("#entryImage").change(function() {
                var preview = document.getElementById('upload-preview');
						preview.src = URL.createObjectURL(event.target.files[0]);
						preview.style.display = "block";

				var form_data = new FormData($('#msform')[0]);

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
							console.log(data)
							console.log(data.Vision)
							loadVsionData(data.Vision)

							document.getElementById('entryImageUUID').value=data.UUID;
							document.getElementById('tmpFileName').value=data.TMPFileName;

						},
					});
		});




		  $('#msform').parsley().on('form:validate', function (formInstance) {
		  		// Allowing for Continuation if the First Block is Valid.
			  	if (formInstance.isValid({group: 'block1', force: true}) == true) {
			  		document.getElementById("reg_sec1_next").disabled = false;
			  		document.getElementById("reg_sec1_next").classList.remove('action-button-deactive');
			  		document.getElementById("reg_sec1_next").classList.add('action-button');
			  	}
			  	else{
			  		document.getElementById("reg_sec1_next").disabled = true;
			  		document.getElementById("reg_sec1_next").classList.remove('action-button');
			  		document.getElementById("reg_sec1_next").classList.add('action-button-deactive');
			  	}
	
			  	// Allowing for Continuation if the Second Block is Valid.
			  	if (formInstance.isValid({group: 'block2', force: true}) == true) {
			  		document.getElementById("reg_sec2_next").disabled = false;
			  		document.getElementById("reg_sec2_next").classList.remove('action-button-deactive');
			  		document.getElementById("reg_sec2_next").classList.add('action-button');



			  	}
			  	else{
			  		document.getElementById("reg_sec2_next").disabled = true;
			  		document.getElementById("reg_sec2_next").classList.remove('action-button');
			  		document.getElementById("reg_sec2_next").classList.add('action-button-deactive');
			  	}
			  	// Allowing for Continuation if the Third Block is Valid.
			  	if (formInstance.isValid({group: 'block3', force: true}) == true) {
			  		document.getElementById("reg_sec3_next").disabled = false;
			  		document.getElementById("reg_sec3_next").classList.remove('action-button-deactive');
			  		document.getElementById("reg_sec3_next").classList.add('action-button');
			  	}
			  	else{
			  		document.getElementById("reg_sec3_next").disabled = true;
			  		document.getElementById("reg_sec3_next").classList.remove('action-button');
			  		document.getElementById("reg_sec3_next").classList.add('action-button-deactive');
			  	}
			  	// Allowing for Continuation if the Third Block is Valid.
			  	if (formInstance.isValid({group: 'block4', force: true}) == true) {
			  		document.getElementById("reg_sec4_next").disabled = false;
			  		document.getElementById("reg_sec4_next").classList.remove('action-button-deactive');
			  		document.getElementById("reg_sec4_next").classList.add('action-button');
			  	}
			  	else{
			  		document.getElementById("reg_sec4_next").disabled = true;
			  		document.getElementById("reg_sec4_next").classList.remove('action-button');
			  		document.getElementById("reg_sec4_next").classList.add('action-button-deactive');
			  	}


		    var ok = formInstance.isValid({group: 'block1', force: true}) || formInstance.isValid({group: 'block2', force: true})|| formInstance.isValid({group: 'block3', force: true});
		    $('.invalid-form-error-message')
		      .html(ok ? '' : 'You must correctly fill *at least one of these two blocks!')
		      .toggleClass('filled', !ok);
		    if (!ok)
		      formInstance.validationResult = false;
		  });
		});