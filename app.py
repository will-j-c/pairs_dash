from dash import dcc, html, Output, Input
import dash_bootstrap_components as dbc
from dotenv import load_dotenv
from server import app, server
from views import dashboard

load_dotenv(override=True)


app.layout = html.Div(
    [
        html.Div([
            html.Div(
                html.Div(id='page-content', className='content'),
                className='content-container'
            ),
        ], className='container-width'),
        dcc.Location(id='url', refresh=False),
    ]
)


@app.callback(Output('page-content', 'children'),
              [Input('url', 'pathname')])
def display_page(pathname):
    if pathname == '/':
        return 'Home'
    # elif pathname == '/login':
    #     return login.layout
    elif pathname == '/dashboard':
        return dashboard.layout
    #     if current_user.is_authenticated:
    #         return success.layout
    #     else:
    #         return login_fd.layout
    # elif pathname == '/logout':
    #     if current_user.is_authenticated:
    #         logout_user()
    #         return logout.layout
    #     else:
    #         return logout.layout
    else:
        return '404'


# @app.callback(
#     Output('user-name', 'children'),
#     [Input('page-content', 'children')])
# def cur_user(input1):
#     if current_user.is_authenticated:
#         return html.Div('Current user: ' + current_user.username)
#         # 'User authenticated' return username in get_id()
#     else:
#         return ''


# @app.callback(
#     Output('logout', 'children'),
#     [Input('page-content', 'children')])
# def user_logout(input1):
#     if current_user.is_authenticated:
#         return html.A('Logout', href='/logout')
#     else:
#         return ''


if __name__ == '__main__':
    app.run(debug=True)
