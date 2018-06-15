
		var emailExists = null;
		var usernameExists = null;

		valid_username = false;
		valid_email = false;
		valid_password1 = false;
		valid_password2 = false;
		valid_firstName = false;
		valid_lastName = false;

		//Add On Key Up Validators. 
		$("#rgst_userName").keyup(function() {
			valid_username = false
			validator = "#validation-text-username"
			if($(this).val().length >= 6){
				if($(this).val().length <= 25){
					var reg_password1 = $(this).val();
					var letters = /^[a-zA-Z0-9]+$/;
					var result = letters.test(reg_password1);
    				if (result == true) {
    					in_data = JSON.stringify({'userName': $(this).val()})
    					console.log(in_data)
    					$.ajax({
						type: 'POST',
						url: '/api/v1.0/existingUserCheck',
						data: in_data,
						contentType: false,
						cache: false,
						processData: false,
						async: true,
						success: function(data) {
							if (data == "True"){
								valid_username = true
								toggleValidationMsg(validator, "Username Available.", true)
							}else{
								toggleValidationMsg(validator, "This username is already taken. Sorry.", false)
							}
						},
						});
   					}
					else{
						toggleValidationMsg(validator, "The username can only contain numbers and letters. Sorry.", false)
					}
				}
				else{
					toggleValidationMsg(validator, "The Username is too long. Must be less than 25 character.", false)
				}
			}
			else{
				toggleValidationMsg(validator, "The Username must be at least 6 characters long.", false)
			}
		});

		$("#rgst_email").keyup(function() {
			valid_email = false
			validator = "#validation-text-email"
			var reg_email = $(this).val();
			var letters = /^([a-zA-Z0-9_.+-])+\@(([a-zA-Z0-9-])+\.)+([a-zA-Z0-9]{2,4})+$/;
			var result = letters.test(reg_email);
			if (result == true) {
				in_data = JSON.stringify({'email': $(this).val()})
				$.ajax({
				type: 'POST',
				url: '/api/v1.0/existingEmailCheck',
				data: in_data,
				contentType: false,
				cache: false,
				processData: false,
				async: true,
				success: function(data) {
					if (data == "True"){
						valid_email = true
						toggleValidationMsg(validator, "Email Address Available.", true)
					}else{
						toggleValidationMsg(validator, "This Email Address is already registered. Sorry.", false)
					}
				},
				});
			}
			else{
				toggleValidationMsg(validator, "The Email Address you have entered look invalid?", false)
			}
		});




		$("#rgst_password1").keyup(function() {
			$("#rgst_password2").val("")
			$("#rgst_password2").prop("disabled",true);
			valid_password1 = false;
			validator = "#validation-text-password"
			if($(this).val().length >= 8){
				if($(this).val().length <= 40){
					var reg_password1 = $(this).val();
					var letters = /[!@#$%^&*()_+.,;:]/;
					var result = letters.test(reg_password1);
    				if (result == true) {
    					var reg_password1 = $(this).val();
						var letters = /[A-Z]/;
						var result = letters.test(reg_password1);
						if (result == true) {
							var reg_password1 = $(this).val();
							var letters = /[0-9]/;
							var result = letters.test(reg_password1);
							if (result == true) {
    							valid_password1 = true
    							$("#rgst_password2").val("")
								$("#rgst_password2").prop("disabled",false);
        						toggleValidationMsg(validator, "Password Valid.", true)
    						}
    						else{
    							toggleValidationMsg(validator, "The password must contain at least 1 number.", false)
    						}
        				}
    					else{
    						toggleValidationMsg(validator, "The password must contain at least 1 capital letter.", false)
    					}
   					}
					else{
						toggleValidationMsg(validator, "The password must contain at least 1 speical character.", false)
					}
				}
				else{
					toggleValidationMsg(validator, "The password is too long. Must be less than 40 character.", false)
				}
			}
			else{
				toggleValidationMsg(validator, "The password must be at least 8 characters long.", false)
			}
		});

		$("#rgst_password2").keyup(function() {
			valid_password2 = false;
			validator = "#validation-text-passwordConfirm"
			if($(this).val() == $("#rgst_password1").val()){
				valid_password2 = true
				toggleValidationMsg(validator, "Passwords match!", true)
			}
			else{
				toggleValidationMsg(validator, "The password do not match. Sorry.", false)
			}
		});


		$("#rgst_firstName").keyup(function() {
			valid_firstName = false;
			validator = "#validation-text-firstName"
			if($(this).val().length >= 2){
				var reg_firstName = $(this).val();
				var letters = /^[a-zA-Z -]+$/;
				var result = letters.test(reg_firstName);
				if(result == true){
					valid_firstName = true
					toggleValidationMsg(validator, "First Name Valid.", true)
				}
				else{
					toggleValidationMsg(validator, "Sorry but your first name can only contain letters.", false)
				}
			}
			else{
				toggleValidationMsg(validator, "Give us at least 2 Character?", false)
			}
		});

		$("#rgst_lastName").keyup(function() {
			valid_lastName = false;
			validator = "#validation-text-lastName"
			if($(this).val().length >= 2){
				var reg_lastName = $(this).val();
				var letters = /^[a-zA-Z -]+$/;
				var result = letters.test(reg_lastName);
				if(result == true){
					valid_lastName = true
					toggleValidationMsg(validator, "Last Name Valid.", true)
				}
				else{
					toggleValidationMsg(validator, "Sorry but your last name can only contain letters.", false)
				}
			}
			else{
				toggleValidationMsg(validator, "Give us at least 2 Characters?", false)
			}
		});





		function toggleValidationMsg(id, msg, valid){
			$(id).css("display", "Block")
			$(id).removeClass();
			$(id).css({fontSize: 12});

			if (valid === true){
		        $(id).addClass("text-success");
	        	$(id).text(msg)
			}
			else{
		        $(id).addClass("text-danger");
	        	$(id).text(msg)
			}
			validateSteps()
		}

		function validateSteps(){
			if (valid_email){
				if (valid_username){
		  			$("#reg_sec1_next").prop("disabled",false);
			  		$("#reg_sec1_next").removeClass('action-button-deactive');
		  			$("#reg_sec1_next").addClass('action-button');
				}else{
		  			$("#reg_sec1_next").prop("disabled",true);
		  			$("#reg_sec1_next").removeClass('action-button');
		  			$("#reg_sec1_next").addClass('action-button-deactive');
				}
			}else{		  			
	  			$("#reg_sec1_next").prop("disabled",true);
		  		$("#reg_sec1_next").removeClass('action-button');
		  		$("#reg_sec1_next").addClass('action-button-deactive');

			}

			if (valid_password1){
				if (valid_password2){
		  			$("#reg_sec2_next").prop("disabled",false);
			  		$("#reg_sec2_next").removeClass('action-button-deactive');
		  			$("#reg_sec2_next").addClass('action-button');
				}else{
		  			$("#reg_sec2_next").prop("disabled",true);
		  			$("#reg_sec2_next").removeClass('action-button');
		  			$("#reg_sec2_next").addClass('action-button-deactive');
				}
			}else{		  			
	  			$("#reg_sec2_next").prop("disabled",true);
		  		$("#reg_sec2_next").removeClass('action-button');
		  		$("#reg_sec2_next").addClass('action-button-deactive');
			}


			if (valid_firstName){
				if (valid_lastName){
		  			$("#reg_sec3_next").prop("disabled",false);
			  		$("#reg_sec3_next").removeClass('action-button-deactive');
		  			$("#reg_sec3_next").addClass('action-button');
				}else{
		  			$("#reg_sec3_next").prop("disabled",true);
		  			$("#reg_sec3_next").removeClass('action-button');
		  			$("#reg_sec3_next").addClass('action-button-deactive');
				}
			}else{		  			
	  			$("#reg_sec3_next").prop("disabled",true);
		  		$("#reg_sec3_next").removeClass('action-button');
		  		$("#reg_sec3_next").addClass('action-button-deactive');
			}
		}






/*		window.Parsley
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
		});*/
