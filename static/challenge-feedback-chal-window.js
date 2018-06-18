$(document).ready(function() {

    var feedbackButton = $("<button>", {
        "id" : "chal-feedback-button",
        "class" : "btn btn-outline-info btn-feedback btn-block",
        "html" : "<small>Leave Feedback</small>",
    });

    var feedbackModal = '<div class="modal fade" tabindex="-1" role="dialog">' +
        '  <div class="modal-dialog" role="document">' +
        '    <div class="modal-content">' +
        '      <div class="modal-header">' +
        '        <h5 class="modal-title">Leave Feedback</h5>' +
        '        <button type="button" class="close" data-dismiss="modal" aria-label="Close">' +
        '          <span aria-hidden="true">&times;</span>' +
        '        </button>' +
        '      </div>' +
        '      <form id="chal-feedback-form" method="POST" action="/chal/\{0\}/feedbacks/answer">' +
        '        <input id="nonce" name="nonce" type="hidden" value="\{1\}">' +
        '        <div class="modal-body">' +
        '          <div id="input-fields"></div>' +
        '        </div>' +
        '        <div class="modal-footer">' +
        '          <button id="feedback-submit-button" type="submit" class="btn btn-primary">Submit</button>' +
        '        </div>' +
        '        <div class="modal-body" style="padding:0 1rem;">' +
        '          <div id="feedback-result-notification" class="alert alert-dismissable text-center w-100" role="alert" style="display: none;">' +
        '            <strong id="feedback-result-message"></strong>' +
        '          </div>' +
        '        </div>' +
        '      </form>' +
        '    </div>' +
        '  </div>' +
        '</div>';

    (function() {
        try {
            var old_updateChalWindow = updateChalWindow;
            updateChalWindow = function(obj) {
                old_updateChalWindow(obj);
                
                $('#chal-window').one('shown.bs.modal', function(e) {
                    updateFeedbackButton(obj);
                    showFeedbackButton();
                });
            }
        } catch (err) {
            console.log('updateChalWindow not defined');
        }

        try {
            var old_renderSubmissionResponse = renderSubmissionResponse;
            renderSubmissionResponse = function (data, cb) {
                old_renderSubmissionResponse(data, cb);
                var result = $.parseJSON(JSON.stringify(data));
                if (result.status == 1) {   // Challenge solved
                    showFeedbackButton();
                    var chalid = feedbackButton.attr("chal-id");
                    loadFeedbackModal(chalid);
                } else if (result.status == 2) { // Challenge already solved
                    showFeedbackButton();
                }
            }
        } catch (err) {
            console.log('renderSubmissionResponse not defined');
        }
    })();

    function updateFeedbackButton(obj) {
        feedbackButton.off('click').on("click", function() {
            loadFeedbackModal(obj.id);
        }).attr("chal-id", obj.id);
    }

    function showFeedbackButton() {
        var chalid = feedbackButton.attr("chal-id");
        $.get(script_root + '/chal/{0}/feedbacks'.format(chalid), function(data) {
            if (data.feedbacks.length > 0) {
                $("#challenge").append(feedbackButton);
            }
        });
    }

    function loadFeedbackModal(chalid) {
        $.get(script_root + '/chal/{0}/feedbacks'.format(chalid), function(data) {
            if (data.feedbacks.length <= 0) {
                return;
            }

            var nonce = $('#nonce').val();
            var res = feedbackModal.format(chalid, nonce);
            var obj = $(res);

            var inputFields = obj.find("#input-fields");

            for (var i = 0; i < data.feedbacks.length; i++) {
                var feedback = data.feedbacks[i];
                
                var formgroup = $("<div>", { class : "form-group" });
                switch(feedback.type) {
                    case 0: // rating
                        var label = $("<label>", {
                            for : "feedback-" + feedback.id,
                            html : feedback.question,
                        });
                        var select = $("<select>", {
                            id : "feedback-" + feedback.id,
                            name : "feedback-" + feedback.id,
                            class : "form-control",
                        }).css("padding", ".375rem .75rem");
                        for (var optioni = 1; optioni <= 5; optioni++) {
                            select.append("<option value='" + optioni + "'>" + optioni + "</option>");
                        }
                        if (feedback.answer != "") {
                            select.val(feedback.answer);
                        }
                        formgroup.append(label);
                        formgroup.append(select);
                        break;
                    case 1: // text
                        var label = $("<label>", {
                            for : "feedback-" + feedback.id,
                            html : feedback.question,
                        });
                        var input = $("<input>", {
                            type : "text",
                            id : "feedback-" + feedback.id,
                            name : "feedback-" + feedback.id,
                            class : "form-control",
                            pattern : ".{1,}",
                            value : feedback.answer,
                        }).prop("required", true)
                          .css("padding", ".375rem .75rem");
                        formgroup.append(label);
                        formgroup.append(input);
                        break;
                }
                inputFields.append(formgroup);
            }
            
            obj.find("#feedback-submit-button").click(function(e) {
                e.preventDefault();
                e.stopPropagation();
                var submitButton = $(this);
                submitButton.addClass("disabled-button");
                submitButton.prop('disabled', true);

                var chalid = feedbackButton.attr("chal-id");
                $.post( script_root + '/chal/' + chalid + '/feedbacks/answer', 
                        obj.find("#chal-feedback-form").serialize(), 
                        function(data) 
                {
                    var result = $.parseJSON(JSON.stringify(data));

                    var result_message = obj.find('#feedback-result-message');
                    var result_notification = obj.find('#feedback-result-notification');
                    result_notification.removeClass();
                    result_message.text(result.message);

                    if (result.status == 0) {           // Success
                        result_notification.addClass('alert alert-success alert-dismissable text-center');
                        result_notification.slideDown();
                    } else if (result.status == 1) {    // Error
                        result_notification.addClass('alert alert-danger alert-dismissable text-center');
                        result_notification.slideDown();
                    }
                });

                setTimeout(function () {
                    $('.alert').slideUp();
                    submitButton.removeClass("disabled-button");
                    submitButton.prop('disabled', false);
                }, 3000);
            });

            $('main').append(obj);

            obj.modal('show');

            $(obj).on('hidden.bs.modal', function(e) {
                $(this).modal('dispose');
            });
        });
    }

});