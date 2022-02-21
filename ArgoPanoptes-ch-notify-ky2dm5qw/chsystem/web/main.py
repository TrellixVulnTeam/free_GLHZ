import os
import api
import secrets
import requests
import utils
import routine

from flask import Flask, render_template, session, request, redirect, Response
from waitress import serve
from paste.translogger import TransLogger
from itertools import islice
from replit import db

routine.delete_logs()
WEBHOOK = os.getenv('WEBHOOK')

app = Flask('', template_folder='chsystem/web/templates',
            static_folder='chsystem/web/static')
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')


@app.route('/')
def home():
    if 'user_id' in session:
        return redirect('dashboard')
    return render_template('index.html')


@app.post('/login')
def login():
    req = request.form
    user = api.login(req['user_id'], req['api_key'])
    if user:
        utils.logger(f'WEB.login: {user["main"]} {req["user_id"]}')
        session['user_id'] = req['user_id']
        session['api_key'] = req['api_key']
        session['main'] = user['main']
        session['role'] = user['role']
        return redirect('dashboard')

    return render_template('index.html', error='Invalid credentials'), 401


@app.get('/logout')
def logout():
    if 'user_id' in session:
        utils.logger(f'WEB.logout: {session["main"]} {session["user_id"]}')
    session.clear()
    return redirect('/')


@app.route('/dashboard')
def dashboard():
    if 'user_id' in session:
        utils.logger(f'WEB.dashboard: {session["main"]} {session["user_id"]}')
        role = session['role']
        return render_template(
            'dashboard.html',
            timers=utils.get_all_timers(),
            timers_default=utils.BOSSES,
            users=api.get_users() if role >= 4 else None,
            roles=api.ROLES,
            role=role,
            role_colors=api.ROLES_COLORS,
            main=session['main'],
            islice=islice,
            enumerate=enumerate,
            minutes_to_dhm=utils.minutes_to_dhm)
    return redirect('/')


@app.route('/logs')
def logs():
    if 'user_id' in session:
        utils.logger(f'WEB.logs: {session["main"]} {session["user_id"]}')
        if session['role'] >= 5:
            logs_db = utils.get_logs().split('\n')
            logs_db.reverse()
            return render_template('logs.html', logs=logs_db)

    return redirect('/')


@app.post('/user/create')
def create_user():
    response = Response()
    request_role = session['role']
    if 'user_id' in session and request_role >= 5:
        req = request.json
        utils.logger(
            f'WEB.user.create: {session["main"]} {session["user_id"]} {req}')
        role = req['role']
        user_id = ''.join(req['user_id'].split())
        main = req['main']
        if role <= 3:
            api_key = api.create_user(user_id, role, main)
            if api_key:
                return api_key
            response.status_code = 409
            return response
        if role == 4 and request_role >= 5:
            api_key = api.create_user(user_id, role, main)
            if api_key:
                return api_key
            response.status_code = 409
            return response

    response.status_code = 401
    return response


@app.post('/user/delete')
def delete_user():
    response = Response()
    response.status_code = 200
    request_role = session['role']
    if 'user_id' in session and request_role >= 5:
        req = request.json
        utils.logger(
            f'WEB.user.delete: {session["main"]} {session["user_id"]} {req}')
        user_id = req['user_id']
        user = api.get_user(user_id)
        if user:
            role = user['role']
            if role <= 3:
                if api.delete_user(user_id):
                    return response
                response.status_code = 404
                return response
            if role == 4 and request_role >= 5:
                if api.delete_user(user_id):
                    return response
                response.status_code = 404
                return response

        response.status_code = 404
        return response

    response.status_code = 401
    return response


@app.post('/user/change-role')
def change_role():
    response = Response()
    response.status_code = 200
    request_role = session['role']
    req = request.json
    role = int(req['role'])
    if 'user_id' in session and request_role >= 5 and role <= 4:
        utils.logger(
            f'WEB.user.change-role: {session["main"]} {session["user_id"]} {req}'
        )
        user_id = req['user_id']
        user = api.get_user(user_id)
        print(user, req)
        if (
            user
            and user['role'] <= 4
            and api.change_role(user_id, role)
        ):
            return response
        response.status_code = 404
        return response
    response.status_code = 401
    return response


@app.post('/boss/sub')
def boss_sub():
    response = Response()
    if 'user_id' in session:
        req = request.json
        utils.logger(
            f'WEB.boss.sub: {session["main"]} {session["user_id"]} {req}')
        if api.boss_sub(session['api_key'], req['boss']):
            response.status_code = 200
        else:
            response.status_code = 404
    else:
        response.status_code = 401
    return response


@app.post('/boss/unsub')
def boss_unsub():
    response = Response()
    if 'user_id' in session:
        req = request.json
        utils.logger(
            f'WEB.boss.unsub: {session["main"]} {session["user_id"]} {req}')
        if api.boss_unsub(session['api_key'], req['boss']):
            response.status_code = 200
        else:
            response.status_code = 404
    else:
        response.status_code = 401
    return response


@app.post('/boss/set')
def boss_reset():
    response = Response()
    if 'user_id' in session:
        req = request.json
        utils.logger(
            f'WEB.boss.set: {session["main"]} {session["user_id"]} {req}')
        boss = req['boss']
        timer = req['timer']
        if api.boss_reset(session['api_key'], boss, timer):
            try:
                api.web_to_discord(boss, timer)
            except Exception as e:
                utils.logger(e)
            response.status_code = 200
        else:
            response.status_code = 404
    else:
        response.status_code = 401
    return response


@app.post('/key/generate')
def key_gen():
    keys = db['keys']
    if 'user_id' in session:
        key = secrets.token_hex(16)
        user_id = session['user_id']
        keys[user_id] = key
        db['keys'] = keys
        print(f'{user_id} generated {key}')
        return key


@app.post('/key/check')
def key_check():
    if 'user_id' in session:
        keys = db['keys']
        req = request.json
        key = req['key']
        user_id = session['user_id']
        if key != keys[user_id]:
            keys[user_id] = key
            db['keys'] = keys
            msg = f'User {session["main"]} {user_id} changed key {key}'
            print(msg)
            requests.post(
                WEBHOOK, data={'username': 'check_key', 'content': msg})
    return 'checked'


def run():
    format_logger = '[%(time)s] %(status)s %(REQUEST_METHOD)s %(REQUEST_URI)s'
    serve(TransLogger(app, format=format_logger),
          host='0.0.0.0',
          port=8080,
          url_scheme='https',
          ident=None)


utils.logger('WEB: started')
run()
