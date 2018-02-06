from __future__ import print_function

import boto3
from boto3.dynamodb.conditions import Key, Attr

import plotly
import plotly.plotly as py
from plotly.graph_objs import *

import numpy as np
from scipy import integrate

# =================
# === AWS SETUP ===
# =================

# Authenticate and setup
#session = boto3.session.Session(profile_name='adminuser')
dynamodb = boto3.resource('dynamodb')#session.resource('dynamodb')
table = dynamodb.Table('sulaSulaProcessed')

# Variables
y_temp = []
x_data = []


# This queries dynamoDB for all items with a certain deviceID IMEI
# Will need to be updated if there is more than one device involved
def queryDynamoDB():
    global y_temp
    global x_data

    # reset global variables
    y_temp = []
    x_data = []
    
    # Query for all items with device ID
    response = table.query(
        KeyConditionExpression=Key('deviceID').eq('AnyNetClickArduino')
    )

    # Keep track of gap between data with these
    current_timestamp = 0
    last_timestamp = 0

    # Loop through each item and create lists
    items = response['Items']
    for item in items:

        # Check to see columns exist
        if ('temperature' in item):

            # If there is no data for more than an hour append None so plotly splits the trace
            current_timestamp = int(item['timestamp'])
            if (current_timestamp-last_timestamp) > 60*1000*60: # 1 hour gap
                y_temp.append(0)
                x_data.append(None)
            last_timestamp = int(item['timestamp'])  # update

            # Append each bit of data to an array
            y_temp.append(float(item['temperature']))
            x_data.append(item['date'])


        # Will execute if required data is not there
        else:
            if not('temperature' in item):
                print('temperature has no entry in this item')

    print('Finished querying. Length or array:', len(y_temp))






# ====================
# === PLOTLY SETUP ===
# ====================

# Authenticate and setup **(MUST CHANGE)**
py.sign_in('username***', 'password**')

# Set up time series plot
def timeSeriesSetUp(data, filename, graph_title, y_axis_label):

    # Parameters for range selector buttons
    selectorOptions=dict(
        buttons=list([
            dict(count=15,
                label='15m',
                step='minute',
                stepmode='backward'),
            dict(count=1,
                label='1h',
                step='hour',
                stepmode='backward'),
            dict(count=6,
                label='6h',
                step='hour',
                stepmode='backward'),
            dict(count=1,
                label='1d',
                step='day',
                stepmode='backward'),
            dict(count=7,
                label='1w',
                step='day',
                stepmode='backward'),
            dict(step='all')
        ])
    )

    # Graph style and parameters
    layout = dict(
        title=graph_title,
        xaxis=dict(
            title = "Time",
            rangeselector = selectorOptions,
            titlefont=dict(
                family = "Arial",
                size = 18,
                color = "#7f7f7f"
            ),

            #rangeslider=dict()
        ),
        yaxis=dict(
            title = y_axis_label,
            titlefont=dict(
                family = "Arial",
                size = 18,
                color = "#7f7f7f"
            )
        )
    )

    print('Sending ' + filename + ' to Plotly now.')
    fig = dict(data=data, layout=layout)
    py.plot(fig, filename=filename)
    print('Sent ' + filename)

# This sends the data received from dynamnoDB to plotly every 20 mins
def sendDataToPlotly():

    # Global variables which contain the queried data
    global y_temp
    global x_data

    # Trace parameters

    # === VOLTAGE GRAPH ===
    temp_trace1 = Scatter(
        x=x_data,
        y=y_temp,
        name = 'Temp',
        connectgaps = False,
        line = dict(
            color = ('#1F77B4'),
            width = 3,
            shape = 'spline')
    )
    print('TEMP PLOT')
    temp_data = Data([temp_trace1])
    timeSeriesSetUp(data=temp_data, filename='01_Temperature_Graph', graph_title='Temperature vs Time',
                    y_axis_label='Temperature (C)')


# ==================
# === AWS LAMBDA ===
# ==================

print('Loading function')
count = 0 # initialise counter
request_id = 'NA'

# Function that runs every time the lambda function is triggered
def lambda_handler(event, context):
    global count
    global request_id

    if request_id == context.aws_request_id:
        print('Same request ID, doing nothing')
    else:
        request_id = context.aws_request_id

        # Loop through each record that the trigger sends for each event
        for num, record in enumerate(event['Records']):

            # Only interested in the insert event so increment counter
            if record['eventName'] == 'INSERT':
                print("Event Number: " + str(num) + " (INSERT)")
                count = count + 1
                print('Count: ', count)
            else:
                print("Event Number: " + str(num) + " (" + record['eventName'] +')')


        if count >= 1:
            # Query and send data
            queryDynamoDB()
            sendDataToPlotly()
            print('Reset counter')
            count = 0 # reset counter
            print('Successfully sent to plotly.')
            return 'Successfully sent to plotly.'

        else:
            print('Waiting for counter before sending to plotly.')
            return 'Waiting for counter before sending to plotly.'



