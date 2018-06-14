from flask import (
    abort,
    request,
    render_template,
    redirect,
    jsonify,
    Blueprint,
    url_for,
    Response,
    session
)

import datetime

from CTFd import utils, challenges
from CTFd.models import db, Challenges, Teams
from CTFd.utils import admins_only, is_admin, authed_only

from sqlalchemy.sql import or_, expression

class ChallengeFeedbackQuestions(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    chalid = db.Column(db.Integer, db.ForeignKey('challenges.id'))
    question = db.Column(db.String(100), nullable=False)
    inputtype = db.Column(db.Integer)

    def __init__(self, chalid, question, inputtype):
        self.chalid = chalid
        self.question = question
        self.inputtype = inputtype

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
            feedbacks.append({'id': feedback.id, 'question': feedback.question, 'type': feedback.inputtype})
        data = {}
        data['feedbacks'] = feedbacks
        return jsonify(data)



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
                        'type': feedback.inputtype
                    })
                return jsonify({'results': json_data})
            elif request.method == 'POST':
                question = request.form.get('question')
                chalid = int(request.form.get('chal'))
                inputtype = int(request.form.get('type') or 0)
                feedback = ChallengeFeedbackQuestions(chalid=chalid, question=question, inputtype=inputtype)
                db.session.add(feedback)
                db.session.commit()
                json_data = {
                    'id': feedback.id,
                    'chalid': feedback.chalid,
                    'question': feedback.question,
                    'type': feedback.inputtype
                }
                db.session.close()
                return jsonify(json_data)