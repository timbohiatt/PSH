//Globals 
data_entryID = null; 


window.onload = function() {
    $("#uploadProcessing").attr("src",("/static/img/processing.gif"))
    loadNextJudgment()
};


$('#judge-approve').click(function() {
    processApproval(1)
});

$('#judge-reject').click(function() {
    processApproval(0)
});




function initItem(data){
    console.log(data.Entry)
    //document.getElementById('judgmentTitle').innerHTML=data.Entry.entryTitle;
    //document.getElementById('judgmentDescription').innerHTML=data.Entry.entryDescription;
    //document.getElementById('judgmentPointValue').innerHTML=data.Entry.entryTitle;
    //document.getElementById('judgmentCategory').innerHTML=data.Entry.entryTitle;
    //document.getElementById('judgmentEntryDT').innerHTML=data.Entry.entry_date;
    //document.getElementById('judgmentEntryOverallStatus').innerHTML=data.Entry.overallStatus;
    var preview = document.getElementById('judgmentImg');
    preview.src = (data.Entry.smallURL);
    //Set Global Entry ID.
    data_entryID = data.Entry.entryID;
   
}


function loadNextJudgment(){
    $("#judgmentImg").css("display", "none");
    $("#uploadProcessing").css("display", "block");

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
                console.log(data.Entry.smallURL)
                if (data.Entry.smallURL != null) {
                    $(function() {
                        initItem(data)
                    }).promise().done(function(){
                        $("#uploadProcessing").css("display", "none");
                        $("#judgmentImg").css("display", "block");
                        //$("#entryContainer").fadeIn("slow").promise().done(function(){
                        //    setTimeout(function(){
                        //        $("#judgmentControls").fadeIn("slow")
                        //    }, 500);
                        //});
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
                loadNextJudgment();
            },
            error: function(error) {
                console.log(error);
                //alert("Error: We could not reach the Server.");
                loadNextJudgment();
            }
        }); 
}




