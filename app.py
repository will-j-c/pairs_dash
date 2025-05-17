from dash import dcc, html, Output, Input
import dash_bootstrap_components as dbc
from dotenv import load_dotenv
from server import app
from flask_login import logout_user, current_user
from views import dashboard, login, login_fd, logout, index

load_dotenv(override=True)

header = dbc.Container(
    className='header',
    children=html.Div(
        children=[
            dbc.Container(className='links', children=[
                dbc.Row([
                        dbc.Col(id='user-name'),
                        dbc.Col(id='logout')
                        ])
            ])
        ]
    )
)

app.layout = html.Div(
    [
        header,
        dbc.Container([
            dbc.Container(
                html.Div(id='page-content'),
                class_name='pt-3 pb-3'
            ),
        ]),
        dcc.Location(id='url', refresh=False),
    ]
)


@app.callback(Output('page-content', 'children'),
              [Input('url', 'pathname')])
def display_page(pathname):
    if pathname == '/':
        return index.layout
    elif pathname == '/login':
        return login.layout
    elif pathname == '/dashboard':
        if current_user.is_authenticated:
            return dashboard.layout
        else:
            return login_fd.layout
    elif pathname == '/logout':
        if current_user.is_authenticated:
            logout_user()
            return logout.layout
        else:
            return logout.layout
    else:
        return '404'


@app.callback(
    Output('user-name', 'children'),
    [Input('page-content', 'children')])
def cur_user(input1):
    if current_user.is_authenticated:
        return html.Div('Current user: ' + current_user.username)
    else:
        return ''


@app.callback(
    Output('logout', 'children'),
    [Input('page-content', 'children')])
def user_logout(input1):
    if current_user.is_authenticated:
        return html.A('Logout', href='/logout', className='btn btn-primary')
    else:
        return ''


if __name__ == '__main__':
    app.run(debug=True, port=5000)
