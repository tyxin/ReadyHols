import flask
from flask import Flask, render_template

app = flask.Flask(__name__)

@app.route('/')
def home():
    return render_template('/n-login/home.html')

@app.route('/<user_name>')
def home_user(user_name):
    return render_template('/n-login/home.html', user_welcome="Welcome, "+user_name)

@app.route('/about-us')
def about_us():
    return render_template('/n-login/about-us.html')

@app.route('/contact-us')
def contact_us():
    return render_template('/n-login/contact-us.html')

@app.route('/learn-more')
def learn_more():
    return render_template('/n-login/learn-more.html')

@app.route('/login')
def login():
    return render_template('/n-login/login.html')

@app.route('/sign-up')
def sign_up():
    return render_template('/n-login/sign-up.html')

@app.route('/tutorial')
def tutorial():
    return render_template('/n-login/tutorial.html')

@app.route('/logged/home')
def logged_home():
    return render_template('/login/vacations/vacations.html')

@app.route('/logged/vacations')
def logged_vacations():
    return render_template('/login/vacations/vacations.html')

@app.route('/logged/user')
def logged_user():
    return render_template('/login/user/user.html')

@app.route('/logged/settings')
def logged_settings():
    return render_template('/login/settings/settings.html')

@app.route('/logged/vacations/summary')
def logged_vacations_summary():
    return render_template('/login/vacations/summary/summary.html')

@app.route('/logged/vacations/itinerary')
def logged_vacations_itinerary():
    return render_template('/login/vacations/itinerary/itinerary.html')

@app.route('/logged/vacations/planning')
def logged_vacations_planning():
    return render_template('/login/vacations/planning/planning.html')

@app.route('/logged/vacations/sharing')
def logged_vacations_sharing():
    return render_template('/login/vacations/sharing/sharing.html')

if __name__ == '__main__':
    app.run()
