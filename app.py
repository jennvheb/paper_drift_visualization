from viz import calculate_segments_straight_up, calculate_segments_angles, calculate_shortest_distance, scale_lengths
from app_background import prep_segments_to_display, calculate_lengths
import plotly.graph_objs as go
import dash
from preprocess import preprocess
from dash import html, dcc
import dash_bootstrap_components as dbc
from dash_bootstrap_templates import load_figure_template
import json

ats, infoinggroups=preprocess() # sets window size, directory, and which outlier function to take

app = dash.Dash(external_stylesheets=[dbc.themes.LUX])

load_figure_template('LUX')
server = app.server

total_sum = 0
for sublist in range(len(ats)):
    total_sum += len(ats[0][-1]) # this is for correctly numbering the ats on the legend

#this is the first trace 
first_line_x = list(ats[0][4][0][1].keys())
first_line_y = list(ats[0][4][0][1].values())

@app.callback( # callback function for the drift visualizations that processes clicks on the graph, inputs in scaling and the id of the sensor stream and selected timestamp specified in the url
    [dash.dependencies.Output('90-degrees-method', 'figure'),
     dash.dependencies.Output('shortest-distance-method', 'figure'),
     dash.dependencies.Output('same-timestamp-method', 'figure'),
     dash.dependencies.Output('questionnaire', 'figure')
    ],
    [dash.dependencies.Input('90-degrees-method', 'clickData'),
     dash.dependencies.Input('shortest-distance-method', 'clickData'),
     dash.dependencies.Input('same-timestamp-method', 'clickData'),
     dash.dependencies.Input('questionnaire', 'clickData'),
     dash.dependencies.Input('url', 'pathname'),
     dash.dependencies.Input('scaling-factor90', 'value'),
     dash.dependencies.Input('scaling-factorshortest', 'value'),
     dash.dependencies.Input('scaling-factorsame', 'value')]
)
def update_graphs(clickData90, clickDatashortest, clickdatasame, clickdataquest, pathname, value90, valueshortest, valuesame):
    first_line_x = list(ats[0][4][0][1].keys())
    first_line_y = list(ats[0][4][0][1].values())
    n=0
    match = False
    x_val = None
    markings = []    

    split_path = pathname.strip("/").split("/")
    if len(pathname) > 1:
        dateiname, x_val = split_path
        x_val = float(x_val)
        for n in range(len(ats[0][4])): # iterate through the time series until the ids match
            if str(dateiname) == str(ats[0][4][n][0].split()[0]):
                first_line_x = list(ats[0][4][n][1].keys())
                first_line_y = list(ats[0][4][n][1].values())
                match = True
                break
            if n == len(ats[0][4])-1 and match== False: 
                first_line_x = []
                first_line_y = []
            elif str(dateiname) == "ats_ok":
                first_line_x = ats[0][0][0]
                first_line_y = list(ats[0][1].flatten())
                match = True
                break
            elif str(dateiname) == "ats_nok":
                first_line_x = ats[1][0][0]
                first_line_y = list(ats[1][1].flatten())
                match = True
                break
    if clickData90:
        point = clickData90['points'][0] # clicked data point
        x_val = point['x'] # x-value of point
    if clickDatashortest:
        point = clickDatashortest['points'][0]
        x_val = point['x']
    if clickdatasame:
        point = clickdatasame['points'][0]
        x_val = point['x']
    if x_val != None:
        segments_90 = calculate_segments_angles(first_line_x, first_line_y, ats, x_val, 0.1) # get the drifts 
        segments_to_display_90scaled = scale_lengths(segments_90, value90) # scale the lengths
        segments_to_display_90hover = prep_segments_to_display(segments_to_display_90scaled, segments_90, ats) # obtain the line segments with the hover information

        segments_shortest = calculate_shortest_distance(first_line_x, first_line_y, ats, x_val)
        segments_to_display_shortestscaled = scale_lengths(segments_shortest, valueshortest)
        segments_to_display_shortesthover = prep_segments_to_display(segments_to_display_shortestscaled, segments_shortest, ats)
        segments_same = calculate_segments_straight_up(first_line_x, first_line_y, ats, x_val)
        sec_segments_to_display_samescaled = scale_lengths(segments_same, valuesame)
        sec_segments_to_display_samehover = prep_segments_to_display(sec_segments_to_display_samescaled, segments_same, ats)     
    else:
        segments_to_display_90hover = []
        segments_to_display_shortesthover = []
        sec_segments_to_display_samehover = []

    if clickdataquest: # this is for the last graph used in the questionnaire, where you could click on multiple points on the time series
        point = clickdataquest['points'][0]
        x_val = point['x']
        y_val = point['y']
        if x_val:
            markings = get_the_markings(x_val, y_val)
        else:
            markings = []       
        
    figure90 = { # visualize the 90 degrees drift visualization graph
        'data': [
            {'x': first_line_x, 'y': first_line_y, 'type': 'line', 'name': "trace # " + str(n) + " " + ats[0][4][n][0].split()[1], 'showlegend':True, 'visible': True},
            *segments_to_display_90hover
        ],
        'layout' : {'xaxis':{"title": "time in seconds", "titlefont": {"family": "Arial", "size": 12, "color": "rgb(68, 68, 68)"}, "tickfont" : {"family": "Arial","size":10, "color": "rgb(68, 68, 68)"}, 'range':[-10, 20], 'constrain' : 'domain'}, 'yaxis':{"title": "sensor value in mm","margin-left":"36.5px", "margin-bottom": "7.6px", "titlefont": {"family": "Arial","size": 12, "color": "rgb(68, 68, 68)"}, "tickfont" : {"family": "Arial","size":10, "color": "rgb(68, 68, 68)"}, "scaleanchor":"x", "scaleratio":1},'legend': {"font": {"family": "Arial","size": 10, "color": "rgb(68, 68, 68)"}, 'hoverlabel_align' : 'right', 'margin' : {'l': 20, 'b': 30, 'r': 10, 't': 10}} },
    }

    figureshortest = {
        'data': [
            {'x': first_line_x, 'y': first_line_y, 'type': 'line', 'name': 'trace', 'showlegend':True, 'visible': True},
            *segments_to_display_shortesthover
        ],
        'layout' : {'xaxis':{"title": "time in seconds", "titlefont": {"family": "Arial", "size": 12, "color": "rgb(68, 68, 68)"}, "tickfont" : {"family": "Arial","size":10, "color": "rgb(68, 68, 68)"}, 'range':[-10, 20], 'constrain' : 'domain'}, 'yaxis':{"title": "sensor value in mm","margin-left":"36.5px", "margin-bottom": "7.6px", "titlefont": {"family": "Arial","size": 12, "color": "rgb(68, 68, 68)"}, "tickfont" : {"family": "Arial","size":10, "color": "rgb(68, 68, 68)"}, "scaleanchor":"x", "scaleratio":1},'legend': {"font": {"family": "Arial","size": 10, "color": "rgb(68, 68, 68)"}, 'hoverlabel_align' : 'right', 'margin' : {'l': 20, 'b': 30, 'r': 10, 't': 10}} },
    }

    figuresame = {
        'data': [
            {'x': first_line_x, 'y': first_line_y, 'type': 'line', 'name': 'trace', 'showlegend':True, 'visible': True},
            *sec_segments_to_display_samehover
        ],
        'layout' : {'xaxis':{"title": "time in seconds", "titlefont": {"family": "Arial", "size": 12, "color": "rgb(68, 68, 68)"}, "tickfont" : {"family": "Arial","size":10, "color": "rgb(68, 68, 68)"}, 'range':[-10, 20], 'constrain' : 'domain'}, 'yaxis':{"title": "sensor value in mm","margin-left":"36.5px", "margin-bottom": "7.6px", "titlefont": {"family": "Arial","size": 12, "color": "rgb(68, 68, 68)"}, "tickfont" : {"family": "Arial","size":10, "color": "rgb(68, 68, 68)"}, "scaleanchor":"x", "scaleratio":1},'legend': {"font": {"family": "Arial","size": 10, "color": "rgb(68, 68, 68)"}, 'hoverlabel_align' : 'right', 'margin' : {'l': 20, 'b': 30, 'r': 10, 't': 10}} },
    }
    figurequest = {
        'data': [
            {'x': first_line_x, 'y': first_line_y, 'type': 'line', 'name': 'trace', 'showlegend':True, 'visible': True},
            {'x' : ats[0][0][0], 'y' : list(ats[0][1].flatten()), 'type': 'line', 'name': 'ats ok', 'hoverinfo': 'none', 'showlegend':True, 'visible': True},
            {'x' : ats[1][0][0], 'y' : list(ats[1][1].flatten()), 'type': 'line', 'name': 'ats nok', 'hoverinfo': 'none', 'showlegend':True, 'visible': True},
            *markings
        ],
        'layout' : {'xaxis':{"title": "time in seconds", "titlefont": {"family": "Arial", "size": 12, "color": "rgb(68, 68, 68)"}, "tickfont" : {"family": "Arial","size":10, "color": "rgb(68, 68, 68)"}, 'range':[-10, 20], 'constrain' : 'domain'}, 'yaxis':{"title": "sensor value in mm","margin-left":"36.5px", "margin-bottom": "7.6px", "titlefont": {"family": "Arial","size": 12, "color": "rgb(68, 68, 68)"}, "tickfont" : {"family": "Arial","size":10, "color": "rgb(68, 68, 68)"}, "scaleanchor":"x", "scaleratio":1},'legend': {"font": {"family": "Arial","size": 10, "color": "rgb(68, 68, 68)"}, 'hoverlabel_align' : 'right', 'margin' : {'l': 20, 'b': 30, 'r': 10, 't': 10}} },
    }
    return figure90, figureshortest, figuresame, figurequest


def calculate_graphs_without_updating(id, point): # this is for the method where the drift length is returned in a json, rather than visualized, for internal checking purposes
    for n in range(len(ats[0][4])):
        if str(id) == str(ats[0][4][n][0].split()[0]): # iterate through the time series until the ids match
            first_line_x = list(ats[0][4][n][1].keys()) # this is the x-values of the chosen trace for the point 
            first_line_y = list(ats[0][4][n][1].values()) # this is the y-values of the chosen trace for the point 
            match = True
            break
        if n == len(ats[0][4])-1 and match== False: 
            first_line_x = []
            first_line_y = []
        elif str(id) == "ats_ok":
                first_line_x = ats[0][0][0]
                first_line_y = list(ats[0][1].flatten())
                match = True
                break
        elif str(id) == "ats_nok":
            first_line_x = ats[1][0][0]
            first_line_y = list(ats[1][1].flatten())
            match = True
            break
    fpoint = float(point)
    unedited_angles = calculate_segments_angles(first_line_x, first_line_y, ats, fpoint, 0.1) # calculate the drift 
    segments_lengths90 = calculate_lengths(unedited_angles, ats) # calculate the drift lengths
    
    unedited_shortest = calculate_shortest_distance(first_line_x, first_line_y, ats, fpoint)
    segments_lengthsshortest = calculate_lengths(unedited_shortest, ats)

    unedited_straight = calculate_segments_straight_up(first_line_x, first_line_y, ats, fpoint)
    segments_lengthssame = calculate_lengths(unedited_straight, ats)

    current_data = dict()

    if segments_lengths90: # input for the json body
        current_data['90-degrees-method'] = {'lengths in mm': segments_lengths90}
    if segments_lengthsshortest:
        current_data['shortest-distance-method'] = {'lengths in mm': segments_lengthsshortest}
    if segments_lengthssame:
        current_data['same-timestamp-method'] = {'lengths in mm': segments_lengthssame}
    return current_data

old_id = None
old_point = None
markings = []
def get_the_markings(x_val, y_val):
    markings.append(go.Scatter(x=[x_val], y=[y_val], mode='markers', marker=dict(color='red'), name='x: '+ str(round(x_val, 2)) + ', y: '+ str(round(y_val, 2))))
    return markings

@app.server.route('/<id>/<point>/json') # specify id and point with /json in the url to obtain the json of the drift lenghts between the selected trace and ats ok/nok
def lengths_json(id, point):
    if old_id != id and old_point != point:
        current_data = calculate_graphs_without_updating(id, point)
    response_data = {
        'trace filename': id,
        'selected datapoint': point,
        'data': current_data,
    }
    response = app.server.response_class(
        response=json.dumps(response_data),
        status=200,
        mimetype='application/json'
    )
    current_data.clear()
    return response



fig = go.Figure() # graph where all traces and ats are displayed
ctr = 0
colors = ['lightsteelblue', 'red', 'blue', 'pink', 'orange', 'green', 'brown', 'purple']
for e in range(len(ats)):
        namez = "ats " + str(ats[e][-1])
        fig.add_trace(go.Scatter(x=ats[e][0][0], y=ats[e][1].ravel(), name=namez, line=dict(color=colors[e])))
for i in range(len(ats[0][4])):
        ctr += 1
        namez = "trace " + str(ats[0][4][i][0].split()[0])
        fig.add_trace(go.Scatter(x= list(ats[0][4][i][1].keys()), y=list(ats[0][4][i][1].values()),name=namez, line=dict(color="#999999")))
fig.update_layout(xaxis_title="time in seconds", yaxis_title= "sensor value in mm", font=dict( family = "Arial",size=10, color='rgb(68, 68, 68)'), legend=dict(font=dict( size= 10, color='rgb(68, 68, 68)')))
fig.update_yaxes(scaleanchor = "x", scaleratio = 1)
fig.update_xaxes(range = [-3, 33], constrain = 'domain')


app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    dcc.Store(id='lengths-store', data={'90-degrees-method': None, 'shortest-distance-method': None, 'same-timestamp-method': None}),
    html.H1(children='Drift Visualisation Method', style = {'font-weight': 'bold','textAlign': 'center', 'margin-top':'15px', 'margin-bottom': '15px'}), 
    html.Div([
        html.Div([
            html.P(children='All traces + ats ok + ats nok', style = {'font-weight': 'bold','textAlign': 'left','margin-left':'13px', 'margin-top':'10px', 'margin-bottom': '-3px'}),
            dcc.Graph(
                id='line-graph5',
                figure=fig, style={'width': '120vh', 'height': '95vh'}
            ),
        ],
      )]),
    html.Div([
        html.Div([
            html.P(children='The 90 degree angles method', style = {'font-weight': 'bold','textAlign': 'left','margin-left':'13px', 'margin-top':'10px','margin-bottom': '-3px'}),
            html.Label('Scaling factor (min: 1) ', style = {'textAlign': 'left','margin-left':'13px', 'margin-right':'13px', 'margin-top':'10px','margin-bottom': '-3px'}),
            dcc.Input(id='scaling-factor90', persistence=True, type='number', min=1,  step=1, value=1),
            dcc.Graph(
                id='90-degrees-method',
                style={'width': '70vh', 'height': '95vh'}
            ),
        ],
        style={'width': '50%', 'display': 'inline-block'}),
        html.Div([
            html.P(children='The shortest distance method', style = {'font-weight': 'bold', 'textAlign': 'left','margin-left':'13px', 'margin-top':'10px','margin-bottom': '-3px'}),
            html.Label('Scaling factor (min: 1) ', style = {'textAlign': 'left','margin-left':'13px', 'margin-right':'13px', 'margin-top':'10px','margin-bottom': '-3px'}),

            dcc.Input(id='scaling-factorshortest',persistence=True, type='number', min=1, step=1, value=1),
            dcc.Graph(
                id='shortest-distance-method',
                style={'width': '70vh', 'height': '95vh'}
            ), 
        ],
        style={'width': '50%', 'display': 'inline-block'})]),
        html.Div([
            html.P(children='The same timestamp method', style = {'font-weight': 'bold','textAlign': 'left','margin-left':'13px', 'margin-top':'10px','margin-bottom': '-3px'}),
            html.Label('Scaling factor (min: 1) ', style = {'textAlign': 'left','margin-left':'13px', 'margin-right':'13px', 'margin-top':'10px','margin-bottom': '-3px'}),
            dcc.Input(id='scaling-factorsame',persistence=True, type='number', min=1, step=1, value=1),
            dcc.Graph(
                id='same-timestamp-method',
                style={'width': '70vh', 'height': '95vh'}
            ),
            ],
        style={'width': '50%', 'display': 'inline-block'}),
        html.Div([
            html.P(children='Selected Trace + Ats_ok + Ats_nok', style = {'font-weight': 'bold','textAlign': 'left','margin-left':'13px', 'margin-top':'10px','margin-bottom': '-3px'}),
            dcc.Graph(
                id='questionnaire',
                style={'width': '70vh', 'height': '95vh'}
            ),
        ], 
        style={'width': '50%', 'display': 'inline-block'}),
        ])


if __name__ == '__main__':
    app.run_server(debug=True)


