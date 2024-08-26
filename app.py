from flask import Flask, render_template, request, jsonify, redirect, url_for
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import pandas as pd
import os

app = Flask(__name__)
app.secret_key = 'corecard'  # Change this to a secure secret key
login_manager = LoginManager()
login_manager.init_app(app)

# Data loading
users = {
    'admin': generate_password_hash('123456')  # Change password as needed
}

class User(UserMixin):
    def __init__(self, username):
        self.id = username

@login_manager.user_loader
def load_user(user_id):
    return User(user_id) if user_id in users else None

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        password = request.form.get('password')
        if users.get('admin') and check_password_hash(users['admin'], password):
            user = User('admin')
            login_user(user)
            return redirect(url_for('edit'))
        else:
            return 'Invalid password', 401
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/data')
def get_data():
    file_path = r"C:\Users\Sanidhya.Mitra\Downloads\Book8.xlsx"
    if not os.path.exists(file_path):
        return jsonify({'error': 'File not found'}), 404

    df = pd.read_excel(file_path)
    
    # Filtering rows based on user type
    if not current_user.is_authenticated or current_user.id != 'admin':
        df = df[df['Status'].str.strip() == 'Open']

    data = df.to_dict(orient='records')
    return jsonify(data)

@app.route('/update', methods=['POST'])
@login_required
def update_data():
    data = request.json
    file_path = r"C:\Users\Sanidhya.Mitra\Downloads\Book8.xlsx"
    if not os.path.exists(file_path):
        return jsonify({'error': 'File not found'}), 404
    
    df = pd.read_excel(file_path)

    # Determine which rows to delete
    rows_to_delete = [update['row'] for update in data if update.get('delete')]
    
    # Remove the rows that need to be deleted
    if rows_to_delete:
        df = df.drop(rows_to_delete).reset_index(drop=True)

    # Update remaining rows
    for update in data:
        if not update.get('delete'):
            row_index = update['row']
            col_name = update['column']
            new_value = update['value']
            df.at[row_index, col_name] = new_value
    
    df.to_excel(file_path, index=False)
    return jsonify(success=True)


@app.route('/edit')
@login_required
def edit():
    return render_template('edit.html')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')