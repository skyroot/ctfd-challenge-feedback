# User Guide 

## As an Admin

To configure challenges using this plugin: `CTFd` -> `Admin` -> `Plugins` -> `Challenge Feedback`

> The admin system is guarded at the web interface using JavaScript, and not guarded at the backend. 
Admins should not tamper with the code on his web browser as it may cause undesirable behaviors.

### Create a new feedback question

A feedback question is visible to a user after he solves its corresponding challenge.
One challenge may have more than one feedback question.

1. At the Challenge Feedback page, click 'View feedbacks' icon under the Settings column for the challenge.

1. The 'Challenge Feedbacks' dialog will appear, showing all the existing feedback questions for the challenge.

1. Click 'New Feedback Question' button.

1. Enter your question, answer type, and any other fields, and click 'Add Question'.

### View feedback answers for a feedback question

A feedback answer is a user's response to a feedback question.
Each feedback question can have only one feedback answer per user. 
They can only be viewed by the admin.

1. At the Challenge Feedback page, click 'View feedbacks' under the Settings column for the challenge.

1. The 'Challenge Feedbacks' dialog will appear, showing all the existing feedback questions for the challenge.

1. Click 'View feedback answers' icon for the challenge.

### Delete a feedback question

You can delete a feedback question with all its corresponding feedback answers.

1. At the Challenge Feedback page, click 'View feedbacks' under the Settings column for the challenge.

1. The 'Challenge Feedbacks' dialog will appear, showing all the existing feedback questions for the challenge.

1. Click 'Delete feedback answers' icon for the challenge.

### Export to JSON/CSV file

You can export and download all feedback questions and feedback answers onto your computer.

> JSON files are mainly used for purpose of backup, and is less human-readable.

> CSV files are recommended for using a spreadsheet editor or statistical application.

1. At the Challenge Feedback page, click 'Export to JSON' or 'Export to CSV' button.

## As a User

> Feedback forms are guarded both at the web interface and backend by this plugin. 
Users should not be able to bypass constraints (such as viewing feedback questions for unsolved challenges) by modifying his web browser.

### View feedback questions

When the user solves a challenge for the first time, the feedback form with all its feedback questions will appear automatically.

### Submit feedback answers

When the user submits his feedback answers for the first time for a challenge, it will be added as a new feedback answers visible to admins.

When the user submits his feedback answers for the same challenge for subsequent times, his existing feedback answers will be updated.