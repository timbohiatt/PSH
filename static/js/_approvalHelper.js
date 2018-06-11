//Globals 
data_entryID = null; 


window.onload = function() {
    $("#uploadProcessing").attr("src",("/static/img/processing.gif"))
    $('#judge-rejectConfirm').prop('disabled', true);
    loadNextJudgment()
};


$('#judge-reject-comment').keyup(function() {
    if ($(this).val().length >= 40){ 
        $("#validation-text").removeClass();
        $("#validation-text").css({fontSize: 12});
        $("#validation-text").addClass("text-success");
        $('#validation-text').html("Your comment is a valid length.")
        $('#judge-rejectConfirm').prop('disabled', false)
    }
    else{
        $("#validation-text").removeClass();
        $("#validation-text").css({fontSize: 12});
        $("#validation-text").addClass("text-danger");
        $('#validation-text').html("Your comment is to short.")
        $('#judge-rejectConfirm').prop('disabled', true)
    }
});

$('#judge-approve').click(function() {
    processApproval(1)
});

$('#judge-reject').click(function() {
    $("#judgementControls").css("display", "none");
    $("#rejectionControls").css("display", "block");
    //processApproval(0)
});

$('#judge-rejectConfirm').click(function() {
    processApproval(0)
});

$('#judge-rejectCancel').click(function() {
    $("#rejectionControls").css("display", "none");
    $("#judgementControls").css("display", "block");
    $('#judge-rejectConfirm').prop('disabled', true)
    $('#judge-reject-comment').val("")
});




function initItem(data){
    var preview = document.getElementById('judgmentImg');
    preview.src = (data.Entry.smallURL);
    data_entryID = data.Entry.entryID;
   
}


function loadNextJudgment(){
    $("#Entries").css("display", "none");
    $("#Processing").css("display", "block");
    $('#judge-reject-comment').val("")

    form_data = {}

    $.ajax({
        type: 'POST',
        url: '/api/v1.0/judge/getEntry',
        data: form_data,
        contentType: false,
        cache: false,
        processData: false,
        async: true,
        }).done(function(data){
        //success: function(data) {
            //When Entires Are Available to Judge 
            if (data.Entries == true){
                if (data.Entry.smallURL != null) {
                    $(function() {
                        initItem(data)
                    }).promise().done(function(){
                        //data = JSON.parse(data)
                        setupJudgment(data)
                        $("#Processing").css("display", "none");
                        $("#Entries").css("display", "block");
                    });  
                }
                else{
                    loadNextJudgment()
                } 
            }
            //When There are no entries to Judge
            else{
                $("#Entries").css("display", "none");
                $("#noEntries").css("display", "block");
            }
        })
        .fail(function(xhr) {
            console.log('error', xhr);
            
        });

}

function setupJudgment(data){
    $("#entry-catTitle").html(data.Entry.categoryTitle);
    $("#entry-catDescription").html(data.Entry.categoryDescription);
    $("#entry-catValue").html(data.Entry.categoryValue);
    
}



function processApproval(judgment) {
    $("#Entries").css("display", "none");
    $("#Processing").css("display", "block");
    

    var message = $('#judge-reject-comment').val()
    $.ajax({
            url: '/api/v1.0/entry/approve',
            data:{
                entryID: data_entryID,
                judgment: judgment,
                msg: message
            },
            type: 'POST',
            success: function(response) {
                loadNextJudgment();
            },
            error: function(error) {
                console.log(error);
                loadNextJudgment();
            }
        }); 
}




