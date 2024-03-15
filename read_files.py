import os
import yaml
import dateutil.parser as dp
import traces


def read(directory, folder): # go through the production_status.txt file where the filename and whether the outcome is ok/nok is specified
    filenames = []
    with open(directory, 'r') as lines:
        for events in lines:
            filenames.append((events.split(':')[0], events.split(':')[1])) # divided into filename and ok/nok
    sensordata = query_status_file(filenames, folder)
    time_sequence, all_peinfo = make_traces(sensordata, folder)
    return time_sequence, all_peinfo

def query_status_file(filenames, folder): # go through the files specified in production_status.txt and search for the file containing the sensor data streams contained within
    sensordata = []
    for filename in filenames:
            flag = False
            f = os.path.join(folder, filename[0] + ".xes.yaml") # search in folder for filename
            with open(f, 'r') as stream: # open a file
                for data in yaml.safe_load_all(stream): # all seperated data within the file (e.g. log, event, event, event, ...)
                    if 'event' in data:
                        for k, v in data['event'].items(): 
                            if v == "activity/receiving": 
                                for k, v in data['event']['data']['data_receiver'][0].items():
                                    if k == 'data':  
                                        if 'CPEE-INSTANCE-UUID' in v: # store filename of the file containing the measurements
                                            sensordata.append((v['CPEE-INSTANCE-UUID'], filename[1].rstrip())) 
                                            flag = True
                                            break
                            if flag == True:
                                break
                    if flag == True:
                         break
    return sensordata

def make_traces(sensordata, folder):
    overlog = dict()
    logs = dict() 
    all_peinfo = dict()
    single_peinfo = dict()
    tick = 'a'
    for filename in sensordata:
            f = os.path.join(folder, filename[0] + ".xes.yaml") 
            with open(f, 'r') as stream: # open file with measurements contained
                ctr = 0
                time_sequence = traces.TimeSeries()
                timestampss = traces.TimeSeries()
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
                                                        ctr= 1
                                                    if ctr != 0:
                                                        parsed_2 = dp.parse(v[i]['timestamp'])
                                                        t_in_seconds = parsed_t.timestamp() # here are the seconds
                                                        two_in_seconds = parsed_2.timestamp() 
                                                        time_sequence[two_in_seconds-t_in_seconds] = v[i]['value']
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
                   
                    logs[str(filename[0])+ " " +str(filename[1])] = tmp

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
        all_peinfo['GV12 Machining'] = single_peinfo # process execution information
 
   
    return overlog, all_peinfo

