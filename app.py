from flask import Flask, render_template, jsonify, redirect

app = Flask(__name__)

@app.route('/')
def home():
    return redirect('/setup')

@app.route('/setup')
def setup():
    return render_template('Setup/installationscreen.html')

@app.route('/setup/express')
def express_setup():
    return render_template('Setup/expressinstallationscreen.html')

@app.route('/setup/complete')
def setup_complete():
    return render_template('Setup/installationcomplete.html')

@app.route('/setup/failed')
def setup_failed():
    return render_template('Setup/installationfailed.html')



@app.route('/webb-admin')
def admin_redirect():
    return redirect('/webb-admin/dash')


@app.route('/webb-admin/dash')
def dashboard():
    return render_template('Dashboard/Pages/dashboard.html')

# Add routes for other pages
@app.route('/webb-admin/dash/features')
def features():
    return render_template('Dashboard/Pages/features.html')

@app.route('/webb-admin/dash/settings')
def settings():
    return render_template('Dashboard/Pages/settings.html')

@app.route('/webb-admin/dash/pages')
def pages():
    return render_template('Dashboard/Pages/pages.html')

@app.route('/webb-admin/dash/comments')
def comments():
    return render_template('Dashboard/Pages/comments.html')

@app.route('/webb-admin/dash/ataglance')
def ataglance():
    return render_template('Dashboard/Pages/ataglance.html')

@app.route('/webb-admin/dash/themes')
def themes():
    return render_template('Dashboard/Pages/themes.html')

@app.route('/webb-admin/dash/plugins')
def plugins():
    return render_template('Dashboard/Pages/plugins.html')

@app.route('/webb-admin/dash/posts')
def posts():
    return render_template('Dashboard/Pages/posts.html')

@app.route('/webb-admin/dash/users')
def users():
    return render_template('Dashboard/Pages/users.html')

# Check if setup is needed
def is_setup_needed():
    # TODO: Implement actual setup check logic
    return True

if __name__ == '__main__':
    if is_setup_needed():
        app.run(debug=True, port=5000)
    else:
        app.run(debug=True)
