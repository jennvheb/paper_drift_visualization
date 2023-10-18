from viz import calculate_segments_straight_up, calculate_segments_angles, calculate_shortest_distance
from app_background import get_processinfo, prep_segments_to_display
import plotly.graph_objs as go
import dash
from preprocess import preprocess
from dash import html, dcc
import dash_bootstrap_components as dbc
from dash_bootstrap_templates import load_figure_template
import json
from flask import jsonify
from flask_caching import Cache

ats, infoinggroups=preprocess() # sets window size, directory, and which outlier function to take

app = dash.Dash(external_stylesheets=[dbc.themes.LUX])
app.server.config['CACHE_TYPE'] = 'simple'
cache = Cache(app.server)

load_figure_template('LUX')
server = app.server


timestamps = []
sensorids = []

total_sum = 0

for sublist in range(len(ats)):
    total_sum += len(ats[0][-1]) # this is for correctly numbering the ats on the legend

#this is the first trace 
first_line_x = list(ats[0][4][0][1].keys())
first_line_y = list(ats[0][4][0][1].values())


#this is to keep track of already clicked points
segments_to_display_short = []
segments_to_display_angles = []
sec_segments_to_display_same = []

@app.callback(
    [dash.dependencies.Output('90-degrees-method', 'figure'),
     dash.dependencies.Output('shortest-distance-method', 'figure'),
     dash.dependencies.Output('same-timestamp-method', 'figure'),
     dash.dependencies.Output('lengths-store', 'data')],
    [dash.dependencies.Input('90-degrees-method', 'clickData'),
     dash.dependencies.Input('shortest-distance-method', 'clickData'),
     dash.dependencies.Input('same-timestamp-method', 'clickData'),
     dash.dependencies.Input('url', 'pathname'),
     dash.dependencies.Input('scaling-factor90', 'value'),
     dash.dependencies.Input('scaling-factorshortest', 'value'),
     dash.dependencies.Input('scaling-factorsame', 'value')]
)
def update_graphs(clickData90, clickDatashortest, clickdatasame, pathname, value90, valueshortest, valuesame):
    first_line_x = list(ats[0][4][0][1].keys())
    first_line_y = list(ats[0][4][0][1].values())
    n=0
    segments_lengths90 = []
    segments_lengthssame = []
    segments_lengthsshortest = []

    match = False

    split_path = pathname.strip("/").split("/")
    if len(pathname) > 1:
        dateiname, x_val = split_path
        x_val = float(x_val)
        for n in range(len(ats[0][4])):
          #  print(str(ats[0][4][n][0].split()[0]))
            if str(dateiname) == str(ats[0][4][n][0].split()[0]):
           #     print("yes")
                first_line_x = list(ats[0][4][n][1].keys())
                first_line_y = list(ats[0][4][n][1].values())
                match = True
                break
            if n == len(ats[0][4])-1 and match== False: 
                first_line_x = []
                first_line_y = []
       # print("dateiname", dateiname)
        #   print("n", n)
    if clickData90:
        point = clickData90['points'][0]
        x_val = point['x']
    if x_val:
        if len(segments_to_display_angles) > 0:
            for elem in segments_to_display_angles:
                elem[0]['visible'] = False
        
        distance = 0.1
        segments_to_display5, unedited2, indices_xval = calculate_segments_angles(first_line_x, first_line_y, ats, x_val, value90, distance)
        tstamps, sensids = get_processinfo(infoinggroups, indices_xval)
        segments_to_display6, segments_lengths90 = prep_segments_to_display(segments_to_display5, unedited2, tstamps, sensids, ats)
    else:
            segments_to_display6 = []
    

    if clickDatashortest:
        point = clickDatashortest['points'][0]
        x_val = point['x']
    if x_val:
        if len(segments_to_display_angles) > 0:
            for elem in segments_to_display_angles:
                elem[0]['visible'] = False
        segments_to_displayz, unedited2, indices_xval = calculate_shortest_distance(first_line_x, first_line_y, ats, x_val, valueshortest)
        tstamps, sensids = get_processinfo(infoinggroups, indices_xval)
        segments_to_displayy, segments_lengthsshortest = prep_segments_to_display(segments_to_displayz, unedited2, tstamps, sensids, ats)
    else:
        segments_to_displayy = []
 
   
    if clickdatasame:
        point = clickdatasame['points'][0]
        x_val = point['x']
    if x_val:
        if len(segments_to_display_angles) > 0:
            for elem in segments_to_display_angles:
                elem[0]['visible'] = False
        sec_segments_to_display2, unedited2, indices_xval = calculate_segments_straight_up(first_line_x, first_line_y, ats, x_val, valuesame)
        tstamps, sensids = get_processinfo(infoinggroups, indices_xval)
        sec_segments_to_display, segments_lengthssame = prep_segments_to_display(sec_segments_to_display2, unedited2, tstamps, sensids, ats)            
    else:
        sec_segments_to_display = []
 
    
    # Retrieve current data (or initialize it if it's the first time)
    current_data = dash.callback_context.states.get('lengths-store.data', {})

    # Update lengths store
    if segments_lengths90:
        current_data['90-degrees-method'] = {'lengths in mm': segments_lengths90}
    if segments_lengthsshortest:
        current_data['shortest-distance-method'] = {'lengths in mm': segments_lengthsshortest}
    if segments_lengthssame:
        current_data['same-timestamp-method'] = {'lengths in mm': segments_lengthssame}
  #  print("current data", current_data)
    figure90 = {
        'data': [
            # Your data structure for line-graph3 here
            {'x': first_line_x, 'y': first_line_y, 'type': 'line', 'name': "trace # " + str(n) + " " + ats[0][4][n][0].split()[1], 'showlegend':True, 'visible': True},
            *segments_to_display6
        ],
        'layout' : {'xaxis':{"title": "time in seconds", "titlefont": {"family": "Arial", "size": 12, "color": "rgb(68, 68, 68)"}, "tickfont" : {"family": "Arial","size":10, "color": "rgb(68, 68, 68)"}, 'range':[-10, 20], 'constrain' : 'domain'}, 'yaxis':{"title": "sensor value in mm","margin-left":"36.5px", "margin-bottom": "7.6px", "titlefont": {"family": "Arial","size": 12, "color": "rgb(68, 68, 68)"}, "tickfont" : {"family": "Arial","size":10, "color": "rgb(68, 68, 68)"}, "scaleanchor":"x", "scaleratio":1},'legend': {"font": {"family": "Arial","size": 10, "color": "rgb(68, 68, 68)"}, 'hoverlabel_align' : 'right', 'margin' : {'l': 20, 'b': 30, 'r': 10, 't': 10}} },
    }

    figureshortest = {
        'data': [
            # Your data structure for line-graphx here
            {'x': first_line_x, 'y': first_line_y, 'type': 'line', 'name': 'trace', 'showlegend':True, 'visible': True},
            *segments_to_displayy
        ],
        'layout' : {'xaxis':{"title": "time in seconds", "titlefont": {"family": "Arial", "size": 12, "color": "rgb(68, 68, 68)"}, "tickfont" : {"family": "Arial","size":10, "color": "rgb(68, 68, 68)"}, 'range':[-10, 20], 'constrain' : 'domain'}, 'yaxis':{"title": "sensor value in mm","margin-left":"36.5px", "margin-bottom": "7.6px", "titlefont": {"family": "Arial","size": 12, "color": "rgb(68, 68, 68)"}, "tickfont" : {"family": "Arial","size":10, "color": "rgb(68, 68, 68)"}, "scaleanchor":"x", "scaleratio":1},'legend': {"font": {"family": "Arial","size": 10, "color": "rgb(68, 68, 68)"}, 'hoverlabel_align' : 'right', 'margin' : {'l': 20, 'b': 30, 'r': 10, 't': 10}} },
    }

    figuresame = {
        'data': [
            # Your data structure for line-graphx here
            {'x': first_line_x, 'y': first_line_y, 'type': 'line', 'name': 'trace', 'showlegend':True, 'visible': True},
            *sec_segments_to_display
        ],
        'layout' : {'xaxis':{"title": "time in seconds", "titlefont": {"family": "Arial", "size": 12, "color": "rgb(68, 68, 68)"}, "tickfont" : {"family": "Arial","size":10, "color": "rgb(68, 68, 68)"}, 'range':[-10, 20], 'constrain' : 'domain'}, 'yaxis':{"title": "sensor value in mm","margin-left":"36.5px", "margin-bottom": "7.6px", "titlefont": {"family": "Arial","size": 12, "color": "rgb(68, 68, 68)"}, "tickfont" : {"family": "Arial","size":10, "color": "rgb(68, 68, 68)"}, "scaleanchor":"x", "scaleratio":1},'legend': {"font": {"family": "Arial","size": 10, "color": "rgb(68, 68, 68)"}, 'hoverlabel_align' : 'right', 'margin' : {'l': 20, 'b': 30, 'r': 10, 't': 10}} },
    }
    cache.set('lengths-store', current_data)
    return figure90, figureshortest, figuresame, current_data

# here below



@app.server.route('/<id>/<point>/json')
def lengths_json(id, point):
    # Fetch lengths and graph names from the Store component
    lengths_data = cache.get('lengths-store')
    response_data = {
        'trace filename': id,
        'selected datapoint': point,
        'data': lengths_data if lengths_data else {}
    }
    response = app.server.response_class(
        response=json.dumps(response_data),
        status=200,
        mimetype='application/json'
    )
    return response

#for n in range(len(ats[0][4])):
 #               if dropdown == n:
 #                   first_line_x = list(ats[0][4][n][1].keys())
 #                   first_line_y = list(ats[0][4][n][1].values())

#this is the graph with all traces TODO: change with the accurate shit


fig = go.Figure()
ctr = 0
#for e in range(len(ats)):
for i in range(len(ats[0][4])):
            ctr += 1
            namez = "trace " + str(i)
            fig.add_trace(go.Scatter(x= list(ats[0][4][i][1].keys()), y=list(ats[0][4][i][1].values()),name=namez, line=dict(color="#999999")))
      #      fig.add_trace(go.Scatter(x=ats[e][2][i], y=ats[e][3][i],name=namez, line=dict(color="#999999")))
fig.update_layout(xaxis_title="time in seconds", yaxis_title= "sensor value in mm", font=dict( family = "Arial",size=10, color='rgb(68, 68, 68)'), legend=dict(font=dict( size= 10, color='rgb(68, 68, 68)')))
fig.update_yaxes(scaleanchor = "x", scaleratio = 1)
fig.update_xaxes(range = [-3, 33], constrain = 'domain')

#this is the graph with all ats
colors = ['lightsteelblue', 'red', 'blue', 'pink', 'orange', 'green', 'brown', 'purple']
fig2 = go.Figure()
fig2.add_trace(go.Scatter(x=ats[0][2][0], y=ats[0][3][0], name="trace 1"))
for e in range(len(ats)):
        namez = "ats " + str(ats[e][-1])
        fig2.add_trace(go.Scatter(x=ats[e][0][0], y=ats[e][1].ravel(), name=namez, line=dict(color=colors[e])))
fig2.update_layout(xaxis_title="time in seconds", yaxis_title= "sensor value in mm",   font=dict(family = "Arial", size=10, color='rgb(68, 68, 68)'), legend=dict(font=dict( size= 10, color='rgb(68, 68, 68)')))
fig2.update_yaxes(scaleanchor = "x", scaleratio = 1)
fig2.update_xaxes(range = [-3, 33], constrain = 'domain')


#print("lenght!!", "trace #", n, ats[0][4][0][0])

app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    dcc.Store(id='lengths-store', data={'90-degrees-method': None, 'shortest-distance-method': None, 'same-timestamp-method': None}),
    html.H1(children='Drift Visualisation Method', style = {'font-weight': 'bold','textAlign': 'center', 'margin-top':'15px', 'margin-bottom': '15px'}), 
    html.Div([
        html.Div([
            html.P(children='All traces, unchanged', style = {'font-weight': 'bold','textAlign': 'left','margin-left':'13px', 'margin-top':'10px', 'margin-bottom': '-3px'}),
            dcc.Graph(
                id='line-graph5',
                figure=fig,style={'width': '60vh', 'height': '95vh'}
            ),
        ],
        style={'width': '50%', 'display': 'inline-block'}),
        html.Div([
            html.P(children='Average time series', style = {'font-weight': 'bold','textAlign': 'left', 'margin-left':'13px','margin-top':'10px','margin-bottom': '-3px'}),
            dcc.Graph( 
                id='line-graph4',
                figure=fig2, style={'width': '60vh', 'height': '95vh'}
            ),
        ],
        style={'width': '50%', 'display': 'inline-block'})]),
    html.Div([
       # html.Div([
       #     html.Label('Choose trace to compare:', style = {'textAlign': 'left','margin-left':'13px', 'margin-right':'13px', 'margin-top':'10px','margin-bottom': '-3px'}),
       #         dcc.Dropdown(
       #             id='dropdown',
       #             persistence=True,
       #             #ats[-1][0][0], 'y' : ats[-1][1].ravel()
       #             options=[{'label': "trace # " + str(n) + " " + ats[0][4][n][0], 'value': n} for n in range(len(ats[0][4]))], #???
       #             value= 0  # Set the default value to the first time series
        #        )]),
        html.Div([
            html.P(children='Machining V2: the 90 degree angles method', style = {'font-weight': 'bold','textAlign': 'left','margin-left':'13px', 'margin-top':'10px','margin-bottom': '-3px'}),
            html.Label('Scaling factor (min: 1) ', style = {'textAlign': 'left','margin-left':'13px', 'margin-right':'13px', 'margin-top':'10px','margin-bottom': '-3px'}),
            dcc.Input(id='scaling-factor90', persistence=True, type='number', min=1,  step=1, value=1),
           # html.Label('Offset (min: 0) ', style = {'textAlign': 'left','margin-left':'13px', 'margin-right':'13px', 'margin-top':'10px','margin-bottom': '-3px'}),
           # dcc.Input(id='spacing3', type='number', min=0, step=0.1, value=0),
            dcc.Graph(
                id='90-degrees-method',
                style={'width': '60vh', 'height': '95vh'}
            ),
        ],
        style={'width': '50%', 'display': 'inline-block'}),
        html.Div([
            html.P(children='Machining V2: the shortest distance method', style = {'font-weight': 'bold', 'textAlign': 'left','margin-left':'13px', 'margin-top':'10px','margin-bottom': '-3px'}),
            html.Label('Scaling factor (min: 1) ', style = {'textAlign': 'left','margin-left':'13px', 'margin-right':'13px', 'margin-top':'10px','margin-bottom': '-3px'}),

            dcc.Input(id='scaling-factorshortest',persistence=True, type='number', min=1, step=1, value=1),
        #    html.Label('Offset (min: 0) ', style = {'textAlign': 'left','margin-left':'13px', 'margin-right':'13px', 'margin-top':'10px','margin-bottom': '-3px'}),

         #   dcc.Input(id='spacingx', type='number', min=0, step=0.1, value=0),
            dcc.Graph(
                id='shortest-distance-method',
                style={'width': '60vh', 'height': '95vh'}
            ), 
        ],
        style={'width': '50%', 'display': 'inline-block'})]),
        html.Div([
            html.P(children='Machining V2: the same timestamp method', style = {'font-weight': 'bold','textAlign': 'left','margin-left':'13px', 'margin-top':'10px','margin-bottom': '-3px'}),
            html.Label('Scaling factor (min: 1) ', style = {'textAlign': 'left','margin-left':'13px', 'margin-right':'13px', 'margin-top':'10px','margin-bottom': '-3px'}),
            dcc.Input(id='scaling-factorsame',persistence=True, type='number', min=1, step=1, value=1),
         #   html.Label('Offset (min: 0) ', style = {'textAlign': 'left','margin-left':'13px', 'margin-right':'13px', 'margin-top':'10px','margin-bottom': '-3px'}),
         #   dcc.Input(id='spacing2', type='number', min=0, step=0.1, value=0),
            dcc.Graph(
                id='same-timestamp-method',
                style={'width': '60vh', 'height': '95vh'}
            ),
        ])])


if __name__ == '__main__':
    app.run_server(debug=True)


