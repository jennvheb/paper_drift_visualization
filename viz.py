import numpy as np
from shapely.geometry import LineString, Point, MultiLineString
import math
import sys
import numpy as np


def calculate_shortest_distance(first_line_x, first_line_y,ats, point_x): #code description in thesis
    line_segments = []
    proc_exec = []
    p1 = get_point(first_line_x, first_line_y, point_x)
    line_ts = LineString(np.column_stack((ats[0][0][0], ats[0][1].ravel()))) 
    closest_point = line_ts.interpolate(line_ts.project(p1))
    proc_exec.append(p1.x)
    line_segments.append(((p1.x, p1.y), (closest_point.x, closest_point.y)))
    for n in range(len(ats)-1):
        proc_exec.append(closest_point.x)
        #  p1 = closest_point gone
        line_ts = LineString(np.column_stack((ats[n+1][0][0], ats[n+1][1].ravel()))) 
        closest_point = line_ts.interpolate(line_ts.project(p1))
        line_segments.append(((p1.x, p1.y), (closest_point.x, closest_point.y)))
   #     print(closest_point.x)
        if n == len(ats)-2:
            proc_exec.append(closest_point.x)
            
    #rint(line_segments)
 #   scaled_lengths = scale_lengths(line_segments, scale_factor)
  #  scaled_and_spaced_lengths = add_offset(scaled_lengths,  offset)
    return line_segments, proc_exec
            
def scale_lengths(line_segments, scale_factor):
    diff = []
    scaled_lengths = []
    for z in range(len(line_segments)):
        diff.append(LineString(line_segments[z]).length) # get the original lengths of the line segments
    for d , k in enumerate(diff):
        slps = cst_slope(line_segments[d][0][0], line_segments[d][0][1], line_segments[d][1][0], line_segments[d][1][1]) # getting the slope of the line segment
        #if d == 0:
        #    start = Point(line_segments[0][0][0], line_segments[0][0][1]) # this is what the length should be, slps[d] is the slope it stays the same
        #else:
        #    start = end
        start = Point(line_segments[d][0][0], line_segments[d][0][1])

        dx = k*scale_factor / math.sqrt(1 + math.pow(slps, 2)) # scaling the line and reconstructing it
        dy = slps * dx
        if((line_segments[d][0][0] < line_segments[d][1][0]) or ((line_segments[d][0][0]-line_segments[d][1][0]) == 0 and line_segments[d][0][1] < line_segments[d][1][1])): # if the direction of the original segment is up/right 
            line = LineString([start, (start.x + dx, start.y + dy)])
        else: # if the direction of the original segment is down/left
            line = LineString([start, (start.x - dx, start.y - dy)])
        end = Point(line.coords[-1]) # get the endpoint of the line       
        scaled_lengths.append(((start.x, start.y), (end.x, end.y)))
    return scaled_lengths

def get_point(first_line_x, first_line_y, point_x):
    for u in range(len(first_line_x)-1): # this is the x values of the first time series
        if round(first_line_x[u],2) == round(point_x, 2):
            p1 = Point(first_line_x[u],first_line_y[u])
            return p1 

def get_perp_line(original, p1, dist, line_ts): 
    # find two points on the time series, equidistant from p1
    point1 = original.interpolate(original.project(p1) - dist) 
    point2 = original.interpolate(original.project(p1) + dist) 
    slope = (point2.y - point1.y) / (point2.x - point1.x)
    # find the slope of a line perpendicular to the line passing through point1 and point2
    perpendicular_slope = -1 / slope
    # find the y-intercept of the line perpendicular to the line passing through point1 and point2 and passing through nearest_point
    y_intercept = p1.y - perpendicular_slope * p1.x
    # create a LineString that passes through nearest_point and is perpendicular to the line passing through point1 and point2
    cd = LineString([(p1.x - 100000, perpendicular_slope * (p1.x - 100000) + y_intercept), (p1.x + 100000, perpendicular_slope * (p1.x + 100000) + y_intercept)])
    intersections = cd.intersection(line_ts)
    return intersections

def identify_intersection(intersections, known_point, line_ts): #code description in thesis
    if intersections.geom_type == 'MultiPoint':
        distances_to_known = [known_point.distance(point) for point in list(intersections.geoms)]
        closest_index = distances_to_known.index(min(distances_to_known))
        closest_point = list(intersections.geoms)[closest_index]
    elif intersections.geom_type == 'Point':
        closest_point = intersections
    else:
        closest_point = line_ts.interpolate(line_ts.project(known_point))
    return closest_point
       
def calculate_segments_angles(first_line_x, first_line_y, ats, point_x): #code description in thesis
    line_segments = []
    proc_exec = []
    dist = 0.1
    p1 = get_point(first_line_x, first_line_y, point_x)
  #  original = LineString(np.column_stack((ats[0][2][0], ats[0][3][0]))) # this was before in my thesis
    original = LineString(np.column_stack((first_line_x, first_line_y)))
    line_ts = LineString(np.column_stack((ats[0][0][0], ats[0][1].ravel()))) 
    intersections = get_perp_line(original, p1, dist, line_ts)
    closest_point = identify_intersection(intersections, p1, line_ts)
    proc_exec.append(p1.x)
    line_segments.append(((p1.x, p1.y), (closest_point.x, closest_point.y)))
    for n in range(len(ats)-1): 
        proc_exec.append(closest_point.x)
    #    p1 = closest_point
       # original = LineString(np.column_stack((ats[n][0][0], ats[n][1].ravel())))
        line_ts = LineString(np.column_stack((ats[n+1][0][0], ats[n+1][1].ravel())))
        intersections = get_perp_line(original, p1, dist, line_ts)
        closest_point = identify_intersection(intersections, p1, line_ts)
        line_segments.append(((p1.x, p1.y), (closest_point.x, closest_point.y)))
        if n == len(ats)-2:
            proc_exec.append(closest_point.x)
   # scaled_and_spaced_lengths = add_offset(scaled_lengths, offset)
    return line_segments, proc_exec

def calculate_segments_straight_up(first_line_x, first_line_y, ats, point_x): #code description in thesis
    line_segments = []
    proc_exec = []
    p1 = get_point(first_line_x,first_line_y, point_x)
    proc_exec.append(p1.x)
    tpv = np.interp(p1.x, ats[0][0][0], ats[0][1].ravel()) 
    closest_point = Point(p1.x, tpv)
    line_segments.append(((p1.x, p1.y), (closest_point.x, closest_point.y)))
    for n in range(len(ats)-1):
        
        proc_exec.append(closest_point.x)
     #   p1 = closest_point is out 
 #       print("p1", p1.x)
  #      print("atsx", len(ats[n+1][0][0]))
  #      print("ats_y", len(ats[n+1][1].ravel()))
        tpv = np.interp(p1.x, ats[n+1][0][0], ats[n+1][1].ravel()) 
        closest_point = Point(p1.x, tpv)
        line_segments.append(((p1.x, p1.y), (closest_point.x, closest_point.y)))
        if n == len(ats)-2:
            proc_exec.append(closest_point.x)
  #  scaled_and_spaced_lengths = add_offset(scaled_lengths, offset)
 

    return line_segments, proc_exec

def cst_slope(x1, y1, x2, y2): 
    if(x2 - x1 != 0):
        return (float)(y2-y1)/(x2-x1)
    return sys.maxsize