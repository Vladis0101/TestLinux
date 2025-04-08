import requests
from flask import Flask, render_template, redirect, url_for, request, abort, flash, session
import os
import re
import random
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps

BASE_DIR = os.path.dirname(__file__)

app = Flask(__name__,
            static_folder=os.path.join(BASE_DIR, 'static'),
            template_folder=os.path.join(BASE_DIR, 'templates'))

app.secret_key = 'SK921'
users_db = {}

WEATHER_API_KEY = "000c71cb345d35d4d9b9282413123cfe"
CITY = "Minsk"
BELARUSIAN_CITIES = {
    'minsk': 'Минск',
    'gomel': 'Гомель',
    'grodno': 'Гродно',
    'vitebsk': 'Витебск',
    'brest': 'Брест',
    'mogilev': 'Могилёв',
    'baranovichi': 'Барановичи',
    'bobruisk': 'Бобруйск',
    'pinsk': 'Пинск',
    'orsha': 'Орша'
}

def login_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if 'user' not in session:
            return redirect(url_for('login', next=request.url))
        return f(*args, **kwargs)
    return wrapper

def validate_registration(data):
    errors = {}
    for field in ['first_name', 'last_name', 'username', 'password', 'email', 'age']:
        if not data.get(field):
            errors[field] = 'Это поле обязательно'

    if not re.fullmatch(r'^[а-яА-ЯёЁ\- ]+$', data['first_name']):
        errors['first_name'] = 'Только русские буквы и дефис'
    if not re.fullmatch(r'^[а-яА-ЯёЁ\- ]+$', data['last_name']):
        errors['last_name'] = 'Только русские буквы и дефис'

    if not re.fullmatch(r'^[a-zA-Z0-9_]{6,20}$', data['username']):
        errors['username'] = 'Латиница, цифры и _, от 6 до 20 символов'
    elif data['username'] in users_db:
        errors['username'] = 'Логин уже занят'

    if not re.fullmatch(r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)[a-zA-Z\d]{8,15}$', data['password']):
        errors['password'] = 'Пароль должен содержать 1 строчную, 1 заглавную букву и 1 цифру (8-15 символов)'

    if not re.fullmatch(r'^[^@]+@[^@]+\.[^@]+$', data['email']):
        errors['email'] = 'Некорректный email'

    try:
        age = int(data['age'])
        if age < 12 or age > 100:
            errors['age'] = 'Возраст должен быть от 12 до 100 лет'
    except ValueError:
        errors['age'] = 'Возраст должен быть числом'

    return errors

@app.route('/register/', methods=['GET', 'POST'])
def register():
    if 'user' in session:
        return redirect(url_for('index'))

    if request.method == 'POST':
        user_data = {
            'first_name': request.form.get('first_name', '').strip(),
            'last_name': request.form.get('last_name', '').strip(),
            'username': request.form.get('username', '').strip(),
            'password': request.form.get('password', ''),
            'email': request.form.get('email', '').strip(),
            'age': request.form.get('age', '').strip()
        }

        errors = validate_registration(user_data)

        if not errors:
            users_db[user_data['username']] = {
                'first_name': user_data['first_name'],
                'last_name': user_data['last_name'],
                'password': generate_password_hash(user_data['password']),
                'email': user_data['email'],
                'age': int(user_data['age'])
            }
            flash('Регистрация прошла успешно! Теперь вы можете войти.', 'success')
            return redirect(url_for('login'))

        return render_template('register.html',
                               errors=errors,
                               form_data=user_data)

    return render_template('register.html')

@app.route('/login/', methods=['GET', 'POST'])
def login():
    if 'user' in session:
        return redirect(url_for('index'))

    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')

        user = users_db.get(username)

        if user and check_password_hash(user['password'], password):
            session['user'] = {
                'username': username,
                'first_name': user['first_name'],
                'last_name': user['last_name']
            }

            next_page = request.args.get('next', url_for('index'))
            return redirect(next_page)

        flash('Неверный логин или пароль', 'error')

    return render_template('login.html')

@app.route('/logout/')
def logout():
    session.pop('user', None)
    return redirect(url_for('index'))

@app.route("/")
def index():
    return render_template('index.html')

@app.route('/duck/')
@login_required
def duck():
    try:
        response = requests.get('https://random-d.uk/api/random')
        duck_data = response.json()
        duck_id = duck_data.get('id', random.randint(1, 999))
        duck_image = duck_data.get('url')

        if not duck_image:
            return "Не удалось получить изображение утки", 500

        return render_template('Duck.html',
                               duck_id=duck_id,
                               duck_image=duck_image)
    except Exception as e:
        return f"Ошибка при получении утки: {str(e)}", 500

@app.route('/fox/<int:count>/')
@login_required
def fox(count):
    if count < 1 or count > 10:
        return "Можно запросить только от 1 до 10 лис", 400

    foxes = []
    for _ in range(count):
        try:
            response = requests.get('https://randomfox.ca/floof/', timeout=3)
            fox_data = response.json()
            if 'image' in fox_data:
                foxes.append(fox_data['image'])
        except:
            continue

    if not foxes:
        return "Не удалось загрузить лис", 500

    return render_template('fox.html',
                           count=count,
                           foxes=foxes)

@app.route('/weather-minsk/')
@login_required
def weather():
    try:
        weather_url = f"http://api.openweathermap.org/data/2.5/weather?q={CITY}&appid={WEATHER_API_KEY}&units=metric&lang=ru"
        response = requests.get(weather_url)
        weather_data = response.json()

        if weather_data.get('cod') != 200:
            return f"Ошибка получения погоды: {weather_data.get('message', 'Unknown error')}", 500

        weather_info = {
            'city': weather_data['name'],
            'temp': round(weather_data['main']['temp']),
            'feels_like': round(weather_data['main']['feels_like']),
            'description': weather_data['weather'][0]['description'].capitalize(),
            'icon': weather_data['weather'][0]['icon'],
            'humidity': weather_data['main']['humidity'],
            'wind_speed': weather_data['wind']['speed'],
            'sunrise': datetime.fromtimestamp(weather_data['sys']['sunrise']).strftime('%H:%M'),
            'sunset': datetime.fromtimestamp(weather_data['sys']['sunset']).strftime('%H:%M')
        }

        return render_template('Weather-Minsk.html', weather=weather_info)

    except Exception as e:
        return f"Ошибка при получении погоды: {str(e)}", 500

@app.route('/belarus-cities/')
@login_required
def belarus_cities():
    return render_template('belarus_cities.html', cities=BELARUSIAN_CITIES)

@app.route('/weather/<city>/')
@login_required
def city_weather(city):
    try:
        if city.lower() not in BELARUSIAN_CITIES:
            return abort(404)
        weather_url = f"http://api.openweathermap.org/data/2.5/weather?q={city},BY&appid={WEATHER_API_KEY}&units=metric&lang=ru"
        response = requests.get(weather_url)
        weather_data = response.json()
        if weather_data.get('sys', {}).get('country') != 'BY':
            return abort(404)
        if weather_data.get('cod') != 200:
            return abort(404)

        weather_info = {
            'city': BELARUSIAN_CITIES[city.lower()],
            'temp': round(weather_data['main']['temp']),
                'feels_like': round(weather_data['main']['feels_like']),
            'description': weather_data['weather'][0]['description'].capitalize(),
            'icon': weather_data['weather'][0]['icon'],
            'humidity': weather_data['main']['humidity'],
            'wind_speed': weather_data['wind']['speed'],
            'sunrise': datetime.fromtimestamp(weather_data['sys']['sunrise']).strftime('%H:%M'),
            'sunset': datetime.fromtimestamp(weather_data['sys']['sunset']).strftime('%H:%M')
        }

        return render_template('Weather-Minsk.html', weather=weather_info)

    except Exception as e:
        return render_template('weather_error.html',
                               error=f"Ошибка при получении погоды: {str(e)}"), 500



@app.route("/header_main_floor/")
def header_main_floor():
    return render_template("header_main_floor.html")


@app.errorhandler(404)
def page_not_found(error):
    return render_template('404.html'), 404

if __name__ == '__main__':
    app.run(debug=True)