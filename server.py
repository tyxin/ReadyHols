from flask import Flask, render_template

app = Flask(__name__)


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

@app.route('/search')
def search():
    return render_template('/n-login/search.html')

@app.route('/sign-up')
def sign_up():
    return render_template('/n-login/sign-up.html')

@app.route('/tutorial')
def tutorial():
    return render_template('/n-login/tutorial.html')

if __name__ == '__main__':
    app.run()
