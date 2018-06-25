function load_feedback_modal(method, feedbackid) {
    if (method == 'create') {
        $('#feedback-modal-question').val('');
        $('#feedback-modal-type').prop('selectedIndex', 0);
        $("#feedback-modal").modal();
    }

    else if (method == 'answers') {
        loadanswers(feedbackid, function() {
            $("#feedback-answers-modal").modal();
        });
    }
}


function deletefeedback(feedbackid){
    ezq({
        title: "Delete Question",
        body: "Are you sure you want to delete this question?",
        success: function() {
            $.delete(script_root + '/admin/feedbacks/' + feedbackid, function(data, textStatus, jqXHR){
                if (jqXHR.status == 204){
                    var chalid = $("#update-feedbacks").attr('chal-id');
                    loadfeedbacks(chalid);
                }
            });
        }
    });
}

var FEEDBACK_TYPES = ["Rating", "Text"];

function loadanswers(feedbackid, cb) {
    $.get(script_root + '/admin/feedbacks/{0}/answers'.format(feedbackid), function(data){
        var table = $('#answersboard > tbody');
        table.empty();
        for (var i = 0; i < data.answers.length; i++) {
            var answer = data.answers[i];
            var answer_row = "<tr>" +
            "<td class='answer-team d-table-cell text-center'>{0}</td>".format(answer.team) +
            "<td class='answer-answer d-table-cell text-center w-75'><pre>{0}</pre></td>".format(htmlentities(answer.answer)) +
            "<td class='answer-timestamp d-table-cell text-center'><small>{0}</small></td>".format(answer.timestamp) +
            "</tr>";
            table.append(answer_row);
        }
        if (cb) {
            cb();
        }
    });
}

function loadfeedbacks(chal, cb) {
    $.get(script_root + '/admin/chal/{0}/feedbacks'.format(chal), function(data){
        var table = $('#feedbacksboard > tbody');
        table.empty();
        for (var i = 0; i < data.feedbacks.length; i++) {
            var feedback = data.feedbacks[i];
            var ratinglabels = "";
            if (feedback.type == 0) {
                ratinglabels = " (1 - " + feedback.extraarg1 + ", 5 - " + feedback.extraarg2 + ")";
            }
            var feedback_row = "<tr>" +
            "<td class='feedback-entry d-table-cell w-75'><pre>{0}</pre></td>".format(htmlentities(feedback.question)) +
            "<td class='feedback-type d-table-cell text-center'>{0}</td>".format(FEEDBACK_TYPES[feedback.type] + ratinglabels) +
            "<td class='feedback-settings d-table-cell text-center'>" +
                "<span data-toggle='tooltip' data-placement='top' title='View feedback answers'>" +
                    "<i role='button' class='btn-fa fas fa-chart-bar' onclick=javascript:load_feedback_modal('answers',{0})></i>".format(feedback.id) +
                "</span>&nbsp; &nbsp;" + 
                "<span data-toggle='tooltip' data-placement='top' title='Delete feedback answers'>" +
                    "<i role='button' class='btn-fa fas fa-times' onclick=javascript:deletefeedback({0})></i>".format(feedback.id) +
                "</span></td>" +
            "</tr>";
            table.append(feedback_row);
        }
        $(function () {
            $('[data-toggle="tooltip"]').tooltip()
        })

        if (cb) {
            cb();
        }
    });
}

$(document).ready(function () {
    $('.view-feedback').click(function (e) {
        var chal_id = $(this).attr('chal-id');
        loadfeedbacks(chal_id, function() {
            $("#chal-id-for-feedback").val(chal_id);  // Preload the challenge ID so the form submits properly. Remove in later iterations
            $("#update-feedbacks").attr('chal-id', chal_id);
            $('#update-feedbacks').modal();
        });
    });

    $('#create-feedback').click(function (e) {
        e.preventDefault();
        load_feedback_modal('create');
    });

    $('#feedback-modal-submit').submit(function (e) {
        e.preventDefault();
        var params = {};
        $(this).serializeArray().map(function (x) {
            params[x.name] = x.value;
        });
        $.post(script_root + $(this).attr('action'), params, function (data) {
            loadfeedbacks(params['chal']);
        });
        $("#feedback-modal").modal('hide');
    });

    $('#feedback-modal-type').change(function() {
        $("#rating-high-label").val("");
        $("#rating-low-label").val("");
        if ($(this).val() == "0") {     // Rating of 1 to 5
            $("#rating-labels").show();
        } else {                        // Text input
            $("#rating-labels").hide();
        }
    });

});