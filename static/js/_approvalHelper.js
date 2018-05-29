//Globals 
data_entryID = null; 


window.onload = function() {
  loadNextJudgment()
};


function initItem(data){
    console.log(data.Entry)
    document.getElementById('judgmentTitle').innerHTML=data.Entry.entryTitle;
    document.getElementById('judgmentDescription').innerHTML=data.Entry.entryDescription;
    //document.getElementById('judgmentPointValue').innerHTML=data.Entry.entryTitle;
    //document.getElementById('judgmentCategory').innerHTML=data.Entry.entryTitle;
    document.getElementById('judgmentEntryDT').innerHTML=data.Entry.entry_date;
    document.getElementById('judgmentEntryOverallStatus').innerHTML=data.Entry.overallStatus;
    var preview = document.getElementById('judgmentImg');
    console.log(data.Entry)
    preview.src = (data.Entry.S3imgSmallURL);
    //Set Global Entry ID.
    data_entryID = data.Entry.entryID;
   
}


function loadNextJudgment(){

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
                $(function() {
                    initItem(data)
                }).promise().done(function(){
                    $("#entryContainer").fadeIn("slow").promise().done(function(){
                        setTimeout(function(){
                            $("#judgmentControls").fadeIn("slow")
                        }, 500);
                    });
                });   
            }
            //When There are no entries to Judge
            else{

                $("#judgmentControls").fadeOut("slow").promise().done(function(){
                    setTimeout(function(){
                        $("#noEntryContainer").fadeIn("slow")
                    }, 1000);
                });
            }
        })
        .fail(function(xhr) {
            console.log('error', xhr);
        });

}



function processApproval(judgment) {

    var message = ""
    $.ajax({
            url: '/api/v1.0/entry/approve',
            data:{
                entryID: data_entryID,
                judgment: judgment,
                msg: message
            },
            type: 'POST',
            success: function(response) {
                
                $( "#judgmentControls").fadeOut("slow").promise().done(function(){
                    $( "#entryContainer").fadeOut("slow").promise().done(function(){
                        setTimeout(function(){
                            loadNextJudgment();
                        }, 1000);
                    });
               }); 
            },
            error: function(error) {
                console.log(error);
                //alert("Error: We could not reach the Server.");
                loadNextJudgment();
            }
        }); 
}



