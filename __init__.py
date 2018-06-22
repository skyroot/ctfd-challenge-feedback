from flask import (
    abort,
    request,
    render_template,
    redirect,
    jsonify,
    Blueprint,
    url_for,
    Response,
    session,
    send_file
)

import datafreeze
import dataset
import datetime
import six
import zipfile

from CTFd import utils, challenges
from CTFd.challenges import challenges_view
from CTFd.models import db, Challenges, Teams, Solves, WrongKeys
from CTFd.utils import is_admin, get_app_config
from CTFd.utils.decorators import (
    authed_only,
    admins_only,
    during_ctf_time_only,
    require_verified_emails,
    viewable_without_authentication
)

from sqlalchemy.sql import and_, expression

class ChallengeFeedbackQuestions(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    chalid = db.Column(db.Integer, db.ForeignKey('challenges.id'))
    question = db.Column(db.String(100), nullable=False)
    inputtype = db.Column(db.Integer)
    extraarg1 = db.Column(db.String(100))
    extraarg2 = db.Column(db.String(100))

    def __init__(self, chalid, question, inputtype, extraarg1, extraarg2):
        self.chalid = chalid
        self.question = question
        self.inputtype = inputtype
        self.extraarg1 = extraarg1
        self.extraarg2 = extraarg2

class ChallengeFeedbackAnswers(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    questionid = db.Column(db.Integer, db.ForeignKey('challenge_feedback_questions.id'))
    teamid = db.Column(db.Integer, db.ForeignKey('teams.id'))
    answer = db.Column(db.String(100), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.datetime.utcnow)

    def __init__(self, questionid, teamid, answer):
        self.questionid = questionid
        self.teamid = teamid
        self.answer = answer

def load(app):
    app.db.create_all()
    
    challenge_feedback = Blueprint('challenge_feedback', __name__, template_folder='templates')
    challenge_feedback_static = Blueprint('challenge_feedback_static', __name__, static_folder='static')
    app.register_blueprint(challenge_feedback)
    app.register_blueprint(challenge_feedback_static, url_prefix='/challenge-feedback')

    utils.register_plugin_script("/challenge-feedback/static/challenge-feedback-chal-window.js")

    @app.route('/admin/plugins/challenge-feedback', methods=['GET'])
    @admins_only
    def challenge_feedback_config_view():
        challenges = Challenges.query.all()
        return render_template('challenge-feedback-config.html', challenges=challenges)


    @app.route('/admin/chal/<int:chalid>/feedbacks', methods=['GET'])
    @admins_only
    def admin_chal_feedbacks(chalid):
        feedbacks = []
        for feedback in ChallengeFeedbackQuestions.query.filter_by(chalid=chalid).all():
            feedbacks.append({
                'id': feedback.id, 
                'question': feedback.question, 
                'type': feedback.inputtype,
                'extraarg1' : feedback.extraarg1,
                'extraarg2' : feedback.extraarg2,
            })
        data = {}
        data['feedbacks'] = feedbacks
        return jsonify(data)

    @app.route('/chal/<int:chalid>/feedbacks', methods=['GET'])
    @require_verified_emails
    @viewable_without_authentication(status_code=403)
    def chal_feedbacks(chalid):
        teamid = session.get('id')
        # Get solved challenge ids
        solves = []
        if utils.user_can_view_challenges():
            if utils.authed():
                solves = Solves.query\
                    .join(Teams, Solves.teamid == Teams.id)\
                    .filter(Solves.teamid == session['id'])\
                    .all()
        solve_ids = []
        for solve in solves:
            solve_ids.append(solve.chalid)

        # Return nothing if challenge is not solved
        if chalid not in solve_ids:
            return jsonify([])

        # Otherwise, return the feedback questions
        feedbacks = []
        for feedback in ChallengeFeedbackQuestions.query.filter_by(chalid=chalid).all():
            answer_entry = ChallengeFeedbackAnswers.query.filter(and_(
                ChallengeFeedbackAnswers.questionid==feedback.id, 
                ChallengeFeedbackAnswers.teamid==teamid
            )).first()
            answer = ""
            if answer_entry is not None:
                answer = answer_entry.answer
            feedbacks.append({
                'id': feedback.id, 
                'question': feedback.question, 
                'type': feedback.inputtype,
                'extraarg1' : feedback.extraarg1,
                'extraarg2' : feedback.extraarg2,
                'answer': answer,
            })
        data = {}
        data['feedbacks'] = feedbacks
        return jsonify(data)

    @app.route('/chal/<int:chalid>/feedbacks/answer', methods=['POST'])
    @require_verified_emails
    @viewable_without_authentication(status_code=403)
    def chal_feedback_answer(chalid):
        teamid = session.get('id')
        success_msg = "Thank you for your feedback"

        # Get solved challenge ids
        solves = []
        if utils.user_can_view_challenges():
            if utils.authed():
                solves = Solves.query\
                    .join(Teams, Solves.teamid == Teams.id)\
                    .filter(Solves.teamid == session['id'])\
                    .all()
        solve_ids = []
        for solve in solves:
            solve_ids.append(solve.chalid)

        # Get feedback ids for this challenge
        feedback_ids = []
        for feedback in ChallengeFeedbackQuestions.query.filter_by(chalid=chalid).all():
            feedback_ids.append(feedback.id)

        if (utils.authed() and utils.is_verified() and chalid in solve_ids):
            for name, value in request.form.iteritems():
                name_tokens = name.split("-")
                if name_tokens[0] == "feedback":
                    feedbackid = int(name_tokens[1])
                    if feedbackid not in feedback_ids:
                        return jsonify({
                            'status': 1,
                            'message': "Error: Invalid feedback ID"
                        })

                    existing_feedback = ChallengeFeedbackAnswers.query.filter(and_(
                        ChallengeFeedbackAnswers.questionid==feedbackid, 
                        ChallengeFeedbackAnswers.teamid==teamid
                    )).first()
                    if existing_feedback is not None:
                        db.session.delete(existing_feedback)
                        success_msg = "Your feedback has been updated"

                    feedback_answer = ChallengeFeedbackAnswers(feedbackid, teamid, value)
                    db.session.add(feedback_answer)
                    db.session.commit()
        else:
            return jsonify({
                    'status': 1,
                    'message': "Error: Authentication failed"
                })
                
        return jsonify({
                    'status': 0,
                    'message': success_msg
                })



    @app.route('/admin/feedbacks/<int:feedbackid>/answers', methods=['GET'])
    @admins_only
    def admin_feedback_answers(feedbackid):
        teams = db.session.query(
                    Teams.id,
                    Teams.name
                )
        teamnames = {}
        for team in teams:
            teamnames[team.id] = team.name

        answers = []
        for answer in ChallengeFeedbackAnswers.query.filter_by(questionid=feedbackid).all():
            answers.append({'id': answer.id, 
                            'team': teamnames[answer.teamid], 
                            'answer': answer.answer, 
                            'timestamp': answer.timestamp})
        data = {}
        data['answers'] = answers
        return jsonify(data)

    @app.route('/admin/feedbacks', defaults={'feedbackid': None}, methods=['POST', 'GET'])
    @app.route('/admin/feedbacks/<int:feedbackid>', methods=['GET', 'DELETE'])
    @admins_only
    def admin_feedbacks(feedbackid):
        if feedbackid:
            feedback = ChallengeFeedbackQuestions.query.filter_by(id=feedbackid).first_or_404()

            if request.method == 'DELETE':
                ChallengeFeedbackAnswers.query.filter_by(questionid=feedbackid).delete()
                db.session.delete(feedback)
                db.session.commit()
                db.session.close()
                return ('', 204)

            json_data = {
                'id': feedback.id,
                'chalid': feedback.chalid,
                'question': feedback.question,
                'type': feedback.inputtype
            }
            db.session.close()
            return jsonify(json_data)
        else:
            if request.method == 'GET':
                feedbacks = ChallengeFeedbackQuestions.query.all()
                json_data = []
                for feedback in feedbacks:
                    json_data.append({
                        'id': feedback.id,
                        'chalid': feedback.chalid,
                        'question': feedback.question,
                        'type': feedback.inputtype,
                        'extraarg1' : feedback.extraarg1,
                        'extraarg2' : feedback.extraarg2,
                    })
                return jsonify({'results': json_data})
            elif request.method == 'POST':
                question = request.form.get('question')
                chalid = int(request.form.get('chal'))
                inputtype = int(request.form.get('type') or -1)
                extraarg1 = ""
                extraarg2 = ""
                if inputtype == 0:
                    extraarg1 = request.form.get('ratinglowlabel')
                    extraarg2 = request.form.get('ratinghighlabel')
                feedback = ChallengeFeedbackQuestions(chalid=chalid, question=question, inputtype=inputtype, extraarg1=extraarg1, extraarg2=extraarg2)
                db.session.add(feedback)
                db.session.commit()
                json_data = {
                    'id': feedback.id,
                    'chalid': feedback.chalid,
                    'question': feedback.question,
                    'type': feedback.inputtype,
                    'extraarg1' : feedback.extraarg1,
                    'extraarg2' : feedback.extraarg2,
                }
                db.session.close()
                return jsonify(json_data)

    @app.route('/admin/feedbacks/export', methods=['GET', 'POST'])
    @admins_only
    def admin_export_feedbacks():
        backup = export_feedbacks()
        ctf_name = utils.ctf_name()
        day = datetime.datetime.now().strftime("%Y-%m-%d")
        full_name = "{}.{}_feedbacks.zip".format(ctf_name, day)
        return send_file(backup, as_attachment=True, attachment_filename=full_name)

    @app.route('/admin/feedbacks/export_csv', methods=['GET', 'POST'])
    @admins_only
    def admin_export_feedbacks_csv():
        backup = export_feedbacks_csv()
        ctf_name = utils.ctf_name()
        day = datetime.datetime.now().strftime("%Y-%m-%d")
        full_name = "{}.{}_feedbacks.csv".format(ctf_name, day)
        return send_file(backup, as_attachment=True, attachment_filename=full_name, cache_timeout=5)

def export_feedbacks():
    db = dataset.connect(get_app_config('SQLALCHEMY_DATABASE_URI'))
    segments = ['feedbacks']

    groups = {
        'feedbacks': [
            'challenges',
            'challenge_feedback_questions',
            'challenge_feedback_answers',
        ]
    }

    # Backup database
    backup = six.BytesIO()

    backup_zip = zipfile.ZipFile(backup, 'w')

    for segment in segments:
        group = groups[segment]
        for item in group:
            result = db[item].all()
            result_file = six.BytesIO()
            datafreeze.freeze(result, format='ctfd', fileobj=result_file)
            result_file.seek(0)
            backup_zip.writestr('db/{}.json'.format(item), result_file.read())

    backup_zip.close()
    backup.seek(0)
    return backup

def export_feedbacks_csv():
    output_lines = []
    output_lines.append("challenge_id,challenge,challenge_desc,challenge_category,challenge_maxattempts,challenge_value,team_id,team,team_email,is_solved,solve_timestamp,num_attempts,feedback_question_id,feedback_question,feedback_question_type,feedback_question_arg1,feedback_question_arg2,feedback_answer,feedback_answer_timestamp")
    challenges = Challenges.query.all()
    for challenge in challenges:
        questions = ChallengeFeedbackQuestions.query.filter_by(chalid=challenge.id).all()
        for question in questions:
            teams = Teams.query.all()
            for team in teams:
                solve = Solves.query.filter(and_(Solves.chalid==challenge.id, Solves.teamid==team.id)).first()
                wrongkeys = WrongKeys.query.filter(and_(WrongKeys.chalid==challenge.id, WrongKeys.teamid==team.id)).all()
                answer = ChallengeFeedbackAnswers.query.filter(and_(ChallengeFeedbackAnswers.questionid==question.id, ChallengeFeedbackAnswers.teamid==team.id)).first()
                fields = [challenge.id, challenge.name, challenge.description, challenge.category, challenge.max_attempts, challenge.value]
                fields.extend([team.id, team.name, team.email])
                if solve is None:
                    fields.extend([0, ''])
                    fields.append(len(wrongkeys))
                else:
                    fields.extend([1, solve.date])
                    fields.append(len(wrongkeys) + 1)
                fields.extend([question.id, question.question, ('Rating' if question.inputtype==0 else 'Text'), question.extraarg1, question.extraarg2])
                if answer is None:
                    fields.extend(['', ''])
                else:
                    fields.extend([answer.answer, answer.timestamp])
                output_lines.append(','.join(map(str, fields)))
    return six.StringIO('\n'.join(output_lines))