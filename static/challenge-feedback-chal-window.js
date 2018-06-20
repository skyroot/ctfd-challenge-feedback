$(document).ready(function() {

    var feedbackInlineForm = 
    '    <div id="chal-feedback-group">' +
    '      <hr><h4 class="text-center pb-3">Give Feedback</h4>' +
    '      <form id="chal-feedback-form" method="POST" action="/chal/\{0\}/feedbacks/answer">' +
    '        <input id="nonce" name="nonce" type="hidden" value="\{1\}">' +
    '        <div class="form-group">' +
    '          <div id="input-fields"></div>' +
    '        </div>' +
    '        <div class="form-group">' +
    '          <button id="feedback-submit-button" type="submit" class="btn btn-primary">Submit</button>' +
    '        </div>' +
    '        <div class="form-group">' +
    '          <div id="feedback-result-notification" class="alert alert-dismissable text-center w-100" role="alert" style="display: none;">' +
    '            <strong id="feedback-result-message"></strong>' +
    '          </div>' +
    '        </div>' +
    '      </form>' +
    '    </div>';

    var chalid = -1;
    var visibleFeedbackForm = null;

    (function() {
        try {
            var old_updateChalWindow = updateChalWindow;
            updateChalWindow = function(obj) {
                old_updateChalWindow(obj);
                
                $('#chal-window').one('shown.bs.modal', function(e) {
                    chalid = obj.id;
                    visibleFeedbackForm = null;
                    showFeedbackForm(false);
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
                if (result.status == 1) {           // Challenge first solved
                    showFeedbackForm(true);
                } else if (result.status == 2) {    // Challenge already solved
                    showFeedbackForm(false);
                }
            }
        } catch (err) {
            console.log('renderSubmissionResponse not defined');
        }
    })();

    function showFeedbackForm(isScrollTo = false) {
        if (visibleFeedbackForm != null) {
            return;
        }
        $.get(script_root + '/chal/{0}/feedbacks'.format(chalid), function(data) {
            if (data.feedbacks.length <= 0) {
                return;
            }
            
            var nonce = $('#nonce').val();
            var res = feedbackInlineForm.format(chalid, nonce);
            var obj = $(res);
            visibleFeedbackForm = obj;

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

                        var ratingLowLabel = "";
                        var ratingHighLabel = "";
                        if (feedback.extraarg1 != "") {
                            ratingLowLabel = " - " + feedback.extraarg1;
                        }
                        if (feedback.extraarg2 != "") {
                            ratingHighLabel = " - " + feedback.extraarg2;
                        }
                        select.append("<option value='1'>1" + ratingLowLabel + "</option>");
                        for (var optioni = 2; optioni <= 4; optioni++) {
                            select.append("<option value='" + optioni + "'>" + optioni + "</option>");
                        }
                        select.append("<option value='5'>5" + ratingHighLabel + "</option>");
                        
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
            
            $("#challenge").append(obj);
            obj.hide();
            obj.slideDown(400, function() {
                if (isScrollTo) {
                    setTimeout(function () {
                        $("#chal-window").animate({
                            scrollTop: obj.position().top,
                        }, 400);
                    }, 1500);
                }
            });
        });
    }

});