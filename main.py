import pandas as pd
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import plotly.graph_objs as go
import plotly.express as px


tennis_df = pd.read_csv('atp_matches_2020.csv')

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
server = app.server


player_names = tennis_df.winner_name.unique()
player_names.sort()

win_loss_options = ["Games Won", "Games Lost"]

app.layout = html.Div([

    html.H3("Choose your favorite tennis player to see their stats for games they won/lost!", style={'textAlign': 'center'}),
    html.Br(),
    html.Div([dcc.Dropdown(id='player-select', options=[{'label': i, 'value': i} for i in player_names],
                           value='Novak Djokovic', style={'width': '200px'}),
                dcc.Dropdown(id='wl-select', options=[{'label': i, 'value': i} for i in win_loss_options],
                           value='Games Won', style={'width': '200px'})]),
    html.Br(),
    html.Div(id='player_name'),
    html.Div(id='country_of_origin'),
    html.Div(id='average_ranking'),
    html.Div(id='1st_serve_percentage'),
    html.Div(id='ace_probability'),
    html.Div(id='break_points_saved_percentage'),
    dcc.Graph(id="games_won_chart",style={'width': '70%' }),
    html.Br(),
     dcc.Markdown('''
            >Map below shows total number of players on the ATP list with the same country of origin. 
            '''), 
    html.Div([dcc.Graph(id="country_of_origin_chart", style={'width': '70%'})]),
    dcc.Markdown('''
            >Graph below shows 1st serve percantage on tournament date. Players can play moultiple games in one tournament day. 
            '''),
    dcc.Graph(id="1st_serve_percentage_chart", style={'width': '70%'}),

])


@app.callback(
    Output(component_id='player_name', component_property='children'),
    
    [Input('player-select', 'value')]
)
def update_player_name(input_value):
    return 'Player Name: {}'.format(input_value)


@app.callback(
    Output(component_id='country_of_origin', component_property='children'),
    [Input('player-select', 'value')]
)
def update_player_country_of_origin(input_value):
    origin_country = tennis_df.loc[tennis_df['winner_name']
                                   == input_value, 'winner_ioc'].iloc[0]
    return 'Country of Origin: {}'.format(origin_country)


@app.callback(
    Output(component_id='average_ranking', component_property='children'),
    [Input('player-select', 'value')],
)
def update_average_ranking(input_value):
    temp_ranking_dataframe = tennis_df.loc[tennis_df['winner_name'] == input_value]
    avg_ranking = str(round(temp_ranking_dataframe['winner_rank'].mean(), 1))
    return 'Average 2020 Ranking: {}'.format(avg_ranking)


@app.callback(
    Output(component_id='1st_serve_percentage', component_property='children'),
    [Input('player-select', 'value')],
    [Input('wl-select', 'value')]
)
def update_first_serve_percentage(input_value, wl_value):

    wl_selector = ""
    if wl_value == "Games Won":
        wl_selector = "winner_name"
    if wl_value == "Games Lost":
        wl_selector = "loser_name"

    temp_serve_dataframe = tennis_df.loc[tennis_df[wl_selector] == input_value]
   
    # sum over the column axis.
    total_serves = temp_serve_dataframe['w_svpt'].sum()
    total_1st_serves_won = temp_serve_dataframe['w_1stWon'].sum()
    percentage_1st_serves_won = str(
        round((total_1st_serves_won / total_serves * 100), 2))
    return 'Average 1st Serve Win Percentage: {}'.format(percentage_1st_serves_won)


@app.callback(
    Output(component_id='ace_probability', component_property='children'),
    [Input('player-select', 'value')],
    [Input('wl-select', 'value')]
)
def update_ace_probability(input_value, wl_value):

    wl_selector = ""
    if wl_value == "Games Won":
        wl_selector = "winner_name"
    if wl_value == "Games Lost":
        wl_selector = "loser_name"

    temp_serve_dataframe = tennis_df.loc[tennis_df[wl_selector] == input_value]
    total_serves = temp_serve_dataframe['w_svpt'].sum()
    total_aces = temp_serve_dataframe['w_ace'].sum()
    percentage_aces = str(round((total_aces / total_serves * 100), 2))
    return 'Ace Probability when Serving in Winning Games: {}'.format(percentage_aces)


@app.callback(
    Output(component_id='break_points_saved_percentage',
           component_property='children'),
    [Input('player-select', 'value')],
    [Input('wl-select', 'value')]
)
def update_break_points_saved_percentage(input_value, wl_value):

    wl_selector = ""
    if wl_value == "Games Won":
        wl_selector = "winner_name"
    if wl_value == "Games Lost":
        wl_selector = "loser_name"

    temp_break_points_datafram = tennis_df.loc[tennis_df[wl_selector] == input_value]
    total_break_points_saved = temp_break_points_datafram['w_bpSaved'].sum()
    total_break_points_faced = temp_break_points_datafram['w_bpFaced'].sum()
    percentage_break_points_saved = str(
        round((total_break_points_saved / total_break_points_faced * 100), 2))
    return 'Average Break Point Saved Percentage: {}'.format(percentage_break_points_saved)




@app.callback(
    Output(component_id='games_won_chart',
           component_property='figure'),
    [Input('player-select', 'value')],
    [Input('wl-select', 'value')]
)
def update_games_won_chart(input_value, wl_value):
    temp_df_1 = tennis_df.loc[tennis_df["winner_name"] == input_value]
    temp_df_2 = tennis_df.loc[tennis_df["loser_name"] == input_value]
    
    labels = ["Games Won", "Games Lost"]

    nums = [len(temp_df_1.index), len(temp_df_2.index)]
    
    data = [go.Bar(x=labels, y=nums,
            marker=dict(
            color=['rgb(102,178,255)', 
               'rgb(204,0,0)']))]
    
    fig = go.Figure(data=data)

    fig.update_layout(title="Games won vs. games lost ",
                        font=dict(
                          family="Courier New, monospace",
                          size=18,
                          color="RebeccaPurple"))
    return fig


@app.callback(
   Output(component_id='country_of_origin_chart',
          component_property='figure'),
   [Input('player-select', 'value')],
    [Input('wl-select', 'value')]
)
def update_country_of_origin_chart(input_value, wl_value):
    df = px.data.gapminder().query("year==2007")
    print("Country Chart Head: ", df.head())
    unique_countries = tennis_df.winner_ioc.unique()
    
    print("PANDAS VERSION", pd.__version__)
    
    winner_locations = tennis_df['winner_ioc'].value_counts()
    winner_locs_df = pd.DataFrame(winner_locations).reset_index()
    print("Winner Locs DF: ", winner_locs_df)
    
    winner_locs_df.columns = ['origin_country', 'player_count']
    print("WInner Locations", winner_locs_df.head())

    fig = px.scatter_geo(winner_locs_df, locations="origin_country", color="player_count", hover_name="origin_country", size="player_count", projection="natural earth")
    fig.update_layout(
        title_text = 'Country of origin',
        font=dict(
                          family="Courier New, monospace",
                          size=18,
                          color="RebeccaPurple",
    ))
    return fig




@app.callback(
    Output(component_id='1st_serve_percentage_chart',
           component_property='figure'),
    [Input('player-select', 'value')],
    [Input('wl-select', 'value')]
)
def update_1st_serve_probability_chart(input_value, wl_value):
    print("updating 1st serve chart!")
    wl_selector = ""
    if wl_value == "Games Won":
        wl_selector = "winner_name"
    if wl_value == "Games Lost":
        wl_selector = "loser_name"

    temp_dataframe_1st_serve_chart = tennis_df.loc[tennis_df[wl_selector] == input_value]

    print(temp_dataframe_1st_serve_chart.head())

    temp_dataframe_1st_serve_chart["1st_serve_percentage"] = (
        temp_dataframe_1st_serve_chart['w_1stWon'] / temp_dataframe_1st_serve_chart['w_svpt']) * 100
    temp_dataframe_1st_serve_chart["formatted_date"] = pd.to_datetime(
        temp_dataframe_1st_serve_chart['tourney_date'].astype(str), format='%Y%m%d')

    print(temp_dataframe_1st_serve_chart.head())

    fig = go.Figure([go.Bar(x=temp_dataframe_1st_serve_chart['formatted_date'], y=temp_dataframe_1st_serve_chart['1st_serve_percentage'], marker= dict(color="MediumPurple"))])
    

    fig.update_layout(barmode='stack',
                        title = "1st serve percentage ",
                        font=dict(
                          family="Courier New, monospace",
                          size=18,
                          color="RebeccaPurple"), 
                )
    return fig



if __name__ == '__main__':
    app.run_server(debug=False)