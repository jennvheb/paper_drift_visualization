import math
from shapely.geometry import LineString
import plotly.graph_objs as go
import numpy as np

def calculate_lengths(line_segments, ats): # this method is used to get the lengths of the drift, called when the method should return a json
    segments_length = dict()
    for elem in range(len(line_segments)): # iterate through the line segments
        cmp = LineString([(line_segments[elem][0][0], line_segments[elem][0][1]), (line_segments[elem][1][0], line_segments[elem][1][1])]).length # obtains the lengths of the line segment
        namez = "trace + ats " + str(ats[elem][-1])
        segments_length[namez] = cmp
    return segments_length

def prep_segments_to_display(segments_to_displayz, unedited2, ats): # this method is used, when the drifts are visualized
    segments_to_displayx = []
    for elem, segment in enumerate(segments_to_displayz): # iterate through the line segments
            cmp = LineString([(unedited2[elem][0][0], unedited2[elem][0][1]), (unedited2[elem][1][0], unedited2[elem][1][1])]).length # obtains the lengths of the line segment
            dduration= abs(unedited2[elem][0][0] - unedited2[elem][1][0]) # obtains the "duration" of the drift
            if elem == 0: # the first line segment is with the time series
                namez = "trace + ats " + str(ats[elem][-1])
                segments_to_displayx.append([go.Scatter(x=[segment[0][0]], y=[segment[0][1]],name='x: ' + str(round(segment[0][0], 2)) + ' y: ' + str(round(segment[0][1], 2)),  mode='markers', marker=dict( size=10, color='red'), visible=True)])
            else: namez = "trace + ats " +str(ats[elem][-1])
            if math.isclose(cmp, 0.05) or cmp > 0.05: # if line segment bigger than set threshold, then it becomes thicker
                if len(segment[0]) == 3: # if there is an offset, that changes the x/y inputs
                    segments_to_displayx.append([go.Scatter( # this adds the offset to the visualization
                        x=(segment[0][0],segment[1][0]) , 
                        y=(segment[0][1], segment[1][1]), 
                        showlegend=False, name='', opacity=0.15,  mode='lines', line=dict(width=3), 
                        hovertemplate='x: %{x}'+'<br>y: %{y} ', visible=True)])
                    segments_to_displayx.append([ #this adds the line segments on the visualization, along with the hoverinformation
                        go.Scatter(x=(segment[0][1],segment[0][2] ), y=(segment[1][1], segment[1][2]),name=namez, 
                                   customdata= np.column_stack(((str(cmp),str(cmp)), (str(dduration), str(dduration)))), 
                                   mode='lines+markers', line=dict(width=3), marker=dict(symbol="arrow", size=15, angleref="previous"), 
                                   hovertemplate='x: %{x}'+'<br>y: %{y} ' + '<br>Length in mm: %{customdata[0]}',visible=True)])
                else:
                    segments_to_displayx.append([ #this adds the line segments on the visualization, along with the hoverinformation
                        go.Scatter(x=(segment[0][0],segment[1][0]) , 
                        y=(segment[0][1], segment[1][1]), 
                                   customdata= np.column_stack(((str(cmp),str(cmp)),(str(dduration), str(dduration)))), 
                                   name=namez,  opacity=.8, mode='lines+markers', line=dict(width=3), marker=dict(symbol="arrow", size=15, angleref="previous"),
                                   hovertemplate='x: %{x}'+'<br>y: %{y} ' 
    + '<br>Length in mm: %{customdata[0]}',visible=True)])
            else:
                if len(segment[0]) == 3:
                    segments_to_displayx.append([go.Scatter( # this adds the offset to the visualization
                        x=(segment[0][0],segment[0][1]) , 
                        y=(segment[1][0], segment[1][1]), 
                        showlegend=False, name='', opacity=0.15,  mode='lines', line=dict(width=3), 
                        hovertemplate='x: %{x}'+'<br>y: %{y} ', visible=True)])
                    segments_to_displayx.append([ #this adds the line segments on the visualization, along with the hoverinformation
                        go.Scatter(x=(segment[0][1],segment[0][2] ), y=(segment[1][1], segment[1][2]),name=namez, 
                                   customdata= np.column_stack(((str(cmp),str(cmp)), (str(dduration), str(dduration)))), 
                                   mode='lines+markers', line=dict(width=1.5), marker=dict(symbol="arrow", size=10, angleref="previous"),
                                   hovertemplate='x: %{x}'+'<br>y: %{y} '    + '<br>Length in mm: %{customdata[0]}',visible=True)]),
                else:
                    segments_to_displayx.append([ #this adds the line segments on the visualization, along with the hoverinformation
                        go.Scatter(x=(segment[0][0],segment[1][0]) , 
                        y=(segment[0][1], segment[1][1]), 
                            customdata= np.column_stack(((str(cmp),str(cmp)), (str(dduration), str(dduration)))), 
                            name=namez, opacity=.8, mode='lines+markers', line=dict(width=1.5), marker=dict(symbol="arrow", size=10, angleref="previous"), 
                            hovertemplate='x: %{x}'+'<br>y: %{y} '    + '<br>Length in mm: %{customdata[0]}',visible=True)]),
    segments_to_displayy = [segment for segments_line in segments_to_displayx for segment in segments_line]
    return segments_to_displayy


