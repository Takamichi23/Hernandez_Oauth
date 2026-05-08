from flask import Flask, redirect, url_for, session, jsonify, render_template_string
from authlib.integrations.flask_client import OAuth
import os

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "SECRET_KEY")

oauth = OAuth(app)

# Configure GitHub OAuth
github = oauth.register(
    name='github',
    client_id=os.environ.get("GITHUB_CLIENT_ID", "Ov23liZza4CscXIMD59W"),
    client_secret=os.environ.get("GITHUB_CLIENT_SECRET", "35e9373fa5de380e8843c03676805a794686ea93"),
    access_token_url='https://github.com/login/oauth/access_token',
    authorize_url='https://github.com/login/oauth/authorize',
    api_base_url='https://api.github.com/',
    client_kwargs={'scope': 'user:email'},
)

# Home Page with Login Button
@app.route('/')
def home():
    return render_template_string("""
        <h1>Home Page</h1>
        <a href="/login">
            <button style="padding:10px 20px;font-size:16px;">
                Login with GitHub
            </button>
        </a>
    """)

# Login Route (force HTTP)
@app.route('/login')
def login():
    return github.authorize_redirect(
        url_for('callback', _external=True, _scheme='http')
    )

# Callback Route (force HTTP)
@app.route('/callback')
def callback():
    token = github.authorize_access_token()
    user = github.get('user').json()

    session['user'] = user
    return redirect('/profile')

# Protected Route
@app.route('/profile')
def profile():
    user = session.get('user')

    if not user:
        return redirect('/')

    return render_template_string("""
    <html>
    <head>
        <title>Profile</title>
        <style>
            body {
                margin: 0;
                font-family: Arial, sans-serif;
                background: linear-gradient(135deg, #1f1c2c, #928dab);
                display: flex;
                justify-content: center;
                align-items: center;
                height: 100vh;
                color: #fff;
            }

            .card {
                background: rgba(255, 255, 255, 0.1);
                backdrop-filter: blur(10px);
                border-radius: 15px;
                padding: 30px;
                width: 320px;
                text-align: center;
                box-shadow: 0 8px 20px rgba(0,0,0,0.3);
                transition: transform 0.2s ease;
            }

            .card:hover {
                transform: scale(1.03);
            }

            img {
                width: 120px;
                height: 120px;
                border-radius: 50%;
                border: 3px solid white;
                margin-bottom: 15px;
            }

            h2 {
                margin: 10px 0;
            }

            a {
                color: #00e6e6;
                text-decoration: none;
            }

            a:hover {
                text-decoration: underline;
            }

            .logout-btn {
                margin-top: 20px;
                padding: 10px 20px;
                border: none;
                border-radius: 8px;
                background: #ff4d4d;
                color: white;
                font-size: 15px;
                cursor: pointer;
                transition: 0.3s;
            }

            .logout-btn:hover {
                background: #ff1a1a;
                transform: scale(1.05);
            }
        </style>
    </head>

    <body>

        <div class="card">

            <img src="{{ user['avatar_url'] }}">

            <h2>{{ user['login'] }}</h2>

            <p>ID: {{ user['id'] }}</p>

            <p>
                <a href="{{ user['html_url'] }}" target="_blank">
                    View GitHub Profile
                </a>
            </p>

            <form action="/logout" method="get">
                <button class="logout-btn">Logout</button>
            </form>

        </div>

    </body>
    </html>
    """, user=user)

# Logout
@app.route('/logout')
def logout():
    session.pop('user', None)
    return "Logged out successfully"

# Protected API
@app.route('/api/secure-data')
def secure_data():
    if 'user' not in session:
        return jsonify({"error": "Unauthorized"}), 401

    return jsonify({
        "message": "This is protected secure data.",
        "user": session['user']['login']
    })

if __name__ == '__main__':
    app.run(debug=True)