# Challenge feedback plugin for CTFd

Allows users to give feedback for a challenge after solving it.

[User Guide](docs/user-guide.md)

## Motivation

For instructors to collect feedbacks for challenges to make adjustments or improvements.

## Install

Copy or clone this repository into CTFd/plugins:

`git clone https://github.com/nus-ncl/ctfd-challenge-feedback.git`

## Features

- Create/delete feedback questions for each challenge

- Feedback may be rating of 1 to 5 with custom labels, or text input

- View feedback responses from the admin panel, or export them as a JSON/CSV file

- Users can submit feedbacks and update them on subsequent submissions

- Feedback form is shown automatically after the challenge is solved for the first time

![Admin panel view](/docs/screenshot_1.png)

![Feedback form](/docs/screenshot_2.png)
