# paper_drift_visualization
This code was used to produce the images used in the questionnaire of our paper and during the evaluation stage.
The output of this code is a dash application in which one can specify the ID of the file in the folder containing the sensor data streams.
If no ID is specified, a random trace is shown.

### Example 1: 
appending "/&lt;trace id&gt;" to the url changes the displayed trace on which the drift to the average time series (in the following called ats) nok/ok are displayed to that specific trace. The drift is shown, when a data point is clicked.

### Example 2:
appending "/&lt;trace id&gt;/&lt;timestamp&gt;" to the url changes the displayed trace on which the drift to the ats nok/ok are displayed to that specific trace. The drift is shown on the specified timestamp.

### Example 3:
appending "/&lt;trace id&gt;/&lt;timestamp&gt;/json" to the url changes the trace on which the drift to the ats nok/ok are output in a json file to that specific trace. The drift is shown on the specified timestamp.

### Explanation of the graphs:

**All traces + ats ok + ats nok**: All traces (with their IDs shown in the legend), the average time series containing traces marked as ok and the average time series containing traces marked as nok are displayed.

**The 90 degree angles method**: The specified trace is shown. If either a timestamp is specified in the url or clicked on the graph, the drift between that trace and the ats ok and ats nok is displayed either on the graph (with the exact length on the hover) or as a json. The drift is the result of the 90 degrees drift method. On the visualization, the drifts can be scaled.

**The shortest distance method**:  The specified trace is shown. If either a timestamp is specified in the url or clicked on the graph, the drift between that trace and the ats ok and ats nok is displayed either on the graph (with the exact length on the hover) or as a json. The drift is the result of the shortest distance drift method. On the visualization, the drifts can be scaled.

**The same timestamp method**:  The specified trace is shown. If either a timestamp is specified in the url or clicked on the graph, the drift between that trace and the ats ok and ats nok is displayed either on the graph (with the exact length on the hover) or as a json. The drift is the result of the same timestamp drift method. On the visualization, the drifts can be scaled.

**Selected Trace + Ats_ok + Ats_nok**: The specified trace is shown along with the ats ok and ats nok. Data points can also be clicked, which appear as red dots.

# setup
First, ensure you have Python 3 installed by running 'python3 --version'. If Python 3 is not installed, please install it from the official Python website or your system's package manager. This code is running on Python 3.10.14.

After cloning the repository, create a virtual environment for the project to manage dependencies separately from your global Python installation:
```sh
$ python3 -m venv env
```

To activate the virtual environment, run:

On macOS/Linux:
```sh
$ source env/bin/activate
```
On Windows (Command Prompt):
```cmd
env\Scripts\activate.bat
```

# dependencies
Install all required dependencies (using Python 3.10.14) by running:
```sh
$ pip3 install -r requirements.txt
```

# run code
Once the setup is complete and all dependencies are installed, you can run the application with:
```sh
$ python3 app.py
```
This command starts the application. Follow any additional instructions provided by the application for accessing it in your web browser.
Parameters such as window size, max group size can be changed in preprocessed.py and the critical drift threshold in app_background.py



# credits
This work is very heavily inspired by my bachelor's thesis. "The drift visualization methods are part of my bachelor's thesis "Concept Drift Prediction Based on Event and Sensor Data Streams - An Interactive Drift Visualization Method" at the TUM School of Computation, Information and Technology, Department of Computer Science, Chair of Information Systems and Business Process Management (i17) and based on the concepts and data set presented in F. Stertz, S. Rinderle-Ma, and J. Mangler, “Analyzing process concept drifts based on sensor event streams during runtime", 2020

The folder data which contains yaml.xes-files that can be used as test inputs are owned by the Chair of Information Systems and Business Process Management (i17) at the Technical University of Munich."
