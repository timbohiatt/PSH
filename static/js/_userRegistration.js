
		var emailExists = null;
		var usernameExists = null;


		window.Parsley
		  .addValidator('existingUser', {
		    requirementType: 'string',
		    validateString: function(value, requirement) {
				axios({
					method: 'post',
					url: '/api/v1.0/existingUserCheck',
					data: {userName: value}
				})
				.then(function (response) {

					var bool = response.data === "False"
					//console.log("Response: "+ bool)
					usernameExists = bool
					return true
				})
				.catch(function (error) {
					console.log(error);
				});
		    },
		    messages: {
		      en: 'This username is already registered'
		    }
		  });

		
		window.Parsley
		  .addValidator('existingEmail', {
		    requirementType: 'string',
		    validateString: function(value, requirement) {
				axios({
					method: 'post',
					url: '/api/v1.0/existingEmailCheck',
					data: {email: value}
				})
				.then(function (response) {

					var bool = response.data === "False"
					//console.log("Response: "+ bool)
					emailExists = bool
					return true
				})
				.catch(function (error) {
					console.log(error);
				});
		    },
		    messages: {
		      en: 'This email address is already registered'
		    }
		  });



		$(function () {
		  $('#msform').parsley().on('form:validate', function (formInstance) {
		  		// Allowing for Continuation if the First Block is Valid.
		  		if (usernameExists == true) {
		  			$('#reg_sec1_errMsg_Add').text("This username is already registered!")
		  		}
		  		else if (emailExists == true){
		  			$('#reg_sec1_errMsg_Add').text("This email address is already registered!")
		  		}
		  		else {
		  			$('#reg_sec1_errMsg_Add').text("")
		  		}

			 	if (formInstance.isValid({group: 'block1', force: true}) == true) {
			 		if (usernameExists == false && emailExists == false){
			 			document.getElementById("reg_sec1_errMsg").innerHTML = "";
			  			document.getElementById("reg_sec1_next").disabled = false;
			  			document.getElementById("reg_sec1_next").classList.remove('action-button-deactive');
			  			document.getElementById("reg_sec1_next").classList.add('action-button');
			  			//console.log("Cleared Block 1 " + formInstance.isValid({group: 'block1', force: true}))
			  			}
			  		else{
			  			document.getElementById("reg_sec1_next").disabled = true;
				  		document.getElementById("reg_sec1_next").classList.remove('action-button');
				  		document.getElementById("reg_sec1_next").classList.add('action-button-deactive');
				  		document.getElementById("reg_sec1_errMsg").innerHTML = "This username is already registered!"
				  		}
			  		}
			  	else{
			  		document.getElementById("reg_sec1_next").disabled = true;
			  		document.getElementById("reg_sec1_next").classList.remove('action-button');
			  		document.getElementById("reg_sec1_next").classList.add('action-button-deactive');
			  		document.getElementById("reg_sec1_errMsg").innerHTML = "This username is already registered!"
			  		//console.log("Failed Block 1 " + formInstance.isValid({group: 'block1', force: true}))
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
			 

		    var ok = formInstance.isValid({group: 'block1', force: true}) || formInstance.isValid({group: 'block2', force: true})|| formInstance.isValid({group: 'block3', force: true});
		    $('.invalid-form-error-message')
		      .html(ok ? '' : 'You must correctly fill *at least one of these two blocks!')
		      .toggleClass('filled', !ok);
		    if (!ok)
		      formInstance.validationResult = false;
		  	
		  });
		});
