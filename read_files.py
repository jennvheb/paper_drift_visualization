import os
from time import time
import yaml
import dateutil.parser as dp
import traces
from datetime import timedelta
import copy
import numpy as np
from scipy import signal
import math


# import the files and transform into time series

def read(directory, folder):
    filenames = []

    #get and go through index.txt
#    for filename in os.listdir(directory):
#        if filename.endswith(".txt"):
#            f = os.path.join(directory, filename)
#            with open(f, 'r') as lines:
    with open(directory, 'r') as lines:
     #   next(lines) #skip first line of doc
        for events in lines:
            filenames.append((events.split(':')[0], events.split(':')[1])) # so here are the filenames without the yaml extension
    
 #   print(len(filenames))
    sensordata = query_status_file(filenames, folder)
    time_sequence, all_peinfo = make_traces(sensordata, folder)

    return time_sequence, all_peinfo

def query_status_file(filenames, folder):
    sensordata = []
    for filename in filenames:
            flag = False
            f = os.path.join(folder, filename[0] + ".xes.yaml")
            with open(f, 'r') as stream: # open a file
                for data in yaml.safe_load_all(stream): # all seperated data within the file (e.g. log, event, event, event, ...)
                    if 'event' in data:
                        for k, v in data['event'].items(): 
                            if v == "activity/receiving": 
                                for k, v in data['event']['data']['data_receiver'][0].items():
                                    if k == 'data':  
                                        if 'CPEE-INSTANCE-UUID' in v:
                                            sensordata.append((v['CPEE-INSTANCE-UUID'], filename[1].rstrip()))
                                            flag = True
                                            break
                            if flag == True:
                                break
                    if flag == True:
                         break
                                
                            
                   
                                
#    print(len(sensordata))
#    return
# TODO: we need to add that when one is okay and when one isn't
    return sensordata

def make_traces(sensordata, folder):
    overlog = dict()
    logs = dict() 
    logs2 = dict()
    all_peinfo = dict()
    single_peinfo = dict()
    to_file = dict()
    tick = 'a'
    for filename in sensordata:
            
            f = os.path.join(folder, filename[0] + ".xes.yaml")
            with open(f, 'r') as stream: # open a file
                ctr = 0
                time_sequence = traces.TimeSeries()
                timestampss = traces.TimeSeries()
                time_series = {}

                for data in yaml.safe_load_all(stream): # all seperated data within the file (e.g. log, event, event, event, ...)
                    if 'event' in data:
                        for k, v in data['event'].items(): 
                            if v == "activity/receiving": 
                                for k, v in data['event']['data']['data_receiver'][0].items():
                                    if k == 'data':  
                                        for i in range(len(v)): # one doc in the file
                                            if v[i]['ID'] == 'keyence/measurement':
                                                if v[i]['value'] != 999.99: # filter out 999.99
                                                    if ctr == 0:
                                                        parsed_t = dp.parse(v[0]['timestamp'])
                                                        time_sequence[0] = v[i]['value']
                                                        timestampss[dp.parse(v[i]['timestamp'])] = 0
                                                        time_series[0] = v[i]['value']
                                                        ctr= 1
                                                    if ctr != 0:
                                                        
                                                        parsed_2 = dp.parse(v[i]['timestamp'])
                                                        
                                                        t_in_seconds = parsed_t.timestamp() # here are the seconds
                                                        two_in_seconds = parsed_2.timestamp() 
                                                        time_sequence[two_in_seconds-t_in_seconds] = v[i]['value']
                                                        time_series[two_in_seconds-t_in_seconds] = v[i]['value']

                                                        timestampss[dp.parse(v[i]['timestamp'])] = two_in_seconds-t_in_seconds
                                                        

                                                    
                if len(time_sequence) > 0:

                    regular = time_sequence.sample( #resample the time sequence to equidistant time series
                        sampling_period=0.05,
                        start= time_sequence.first_key(),
                        end= time_sequence.last_key(),
                        interpolate='linear'
                    )
                                                                            
                    tmp = dict()
                    for tme, elem in regular:
                        tmp[tme] = elem
                   
                    logs[filename[1]+str(tick)] = tmp
                    logs2[filename] = time_series
                    regular = timestampss.sample( # resample the process info in same period as the time series
                        sampling_period=0.05,
                        start= timestampss.first_key(),
                        end= timestampss.last_key(),
                        interpolate='linear'
                    )
                                                                            
                    tmp = dict()
                    for tme, elem in regular:
                        tmp[tme] = elem
                    single_peinfo[filename[1]+str(tick)] = tmp
                    tick = chr(ord(tick) + 1)
                    

    if len(logs) > 0:
        overlog['GV12 Machining'] = logs # time series
      #  print(logs2[('85f5c26f-3419-457f-835e-b7ff8ed9e30b', 'ok\n')])
        to_file['GV12 Machining'] = logs2
        f = open("traces_relative.txt", "w")
        f.write(str(to_file))
        f.close()

        all_peinfo['GV12 Machining'] = single_peinfo # process execution information

   
    return overlog, all_peinfo

