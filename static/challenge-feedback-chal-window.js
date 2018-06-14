(function() {
    try {
        var old_updateChalWindow = updateChalWindow;
        updateChalWindow = function(obj) {
            old_updateChalWindow(obj);
            
            $('#chal-window').on('shown.bs.modal', function(e) {
                renderFeedbackQuestions(obj);
            });
        }
    } catch (err) {
        console.log('updateChalWindow not defined');
    }
})();

function renderFeedbackQuestions(obj) {
    var feedbackButton = $("#chal-feedback-button");

    if (feedbackButton.length == 0) {
        feedbackButton = $("<button>", {
            "id" : "chal-feedback-button",
            "class" : "btn btn-outline-info btn-feedback btn-block",
            "html" : "<small>Leave Feedback</small>",
        }).click(function() {
            loadhint(1);
        });
        feedbackButton.hide();
        $("#challenge").append(feedbackButton);
    }

    // get user solve by chalid.
        // if solved, show button with chalid tags.
}