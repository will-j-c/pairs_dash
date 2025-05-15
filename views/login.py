from dash import Input, Output, State, dcc, html
import bcrypt

from server import app, User
from flask_login import login_user

def check_password(input_password, hashed_password):
    # encoding
    input_pass = input_password.encode('utf-8')
    hashed_pass = hashed_password.encode('utf-8')
    if bcrypt.checkpw(input_pass, hashed_pass):
        print('password matched')
        return True
    else:
        print('password not matched')
        return False

layout = html.Div(
    children=[
        html.Div(
            className="container",
            children=[
                dcc.Location(id='url_login', refresh=True),
                html.Div('''Please log in to continue:''', id='h1'),
                html.Div(
                    children=[
                        dcc.Input(
                            placeholder='Enter your username',
                            n_submit=0,
                            type='text',
                            id='uname-box'
                        ),
                        dcc.Input(
                            placeholder='Enter your password',
                            n_submit=0,
                            type='password',
                            id='pwd-box'
                        ),
                        html.Button(
                            children='Login',
                            n_clicks=0,
                            type='submit',
                            id='login-button'
                        ),
                        html.Div(children='', id='output-state')
                    ]
                ),
            ]
        )
    ]
)


@app.callback(Output('url_login', 'pathname'),
              [Input('login-button', 'n_clicks'),
              Input('uname-box', 'n_submit'),
               Input('pwd-box', 'n_submit')],
              [State('uname-box', 'value'),
               State('pwd-box', 'value')])
def success(n_clicks, n_submit_uname, n_submit_pwd, input1, input2):
    user = User.query.filter_by(username=input1).first()
    if user:
        print('#######ID: ', user.password)
        if check_password(input2, user.password):
            login_user(user)
            return '/dashboard'
        else:
            pass
    else:
        pass
