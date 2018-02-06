import boto3
import base64
import datetime
from decimal import *

# SETUP
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('decoded_temperature')  # THIS IS ALL YOU NEED TO CHANGE


# =================================
# === DATA PROCESSING FUNCTIONS ===
# =================================


# Converts base64 (format in AWS) to a value
def base64ToValue(b):
    decoded = base64.b64decode(b).decode('ascii')
    return Decimal(decoded)



# =========================
# === DYNAMODB FUNCTION ===
# =========================

# Writes the data from each 'word' to the table.
def write_data_to_table(temp, deviceID, timestamp):

    # Assign variables
    date_and_time = datetime.datetime.fromtimestamp(int(int(timestamp) / 1000)).strftime('%Y-%m-%d %H:%M:%S')

    # Add the processed data to a new dynamoDB table defined above
    table.put_item(
        Item={
            'date': date_and_time,
            'temperature': temp,
            'deviceID': deviceID,
            'timestamp': timestamp,
        }
    )
    print('Status added to table.')


# ============================
# === MAIN LAMBDA FUNCTION ===
# ============================

print('Loading function')

# Function that runs every time the lambda function is triggered
def lambda_handler(event, context):
    # print("Received event: " + json.dumps(event, indent=2))

    # Loop through each record that the trigger gives in the event
    for num, record in enumerate(event['Records']):

        # Only interested in the INSERT event
        if record['eventName'] == 'INSERT':
            print("Event Number: " + str(num) + " (INSERT)")

            # Variables
            encoded_value = record['dynamodb']['NewImage']['temperature_raw']['B']
            deviceID = record['dynamodb']['NewImage']['deviceID']['S']
            timestamp = record['dynamodb']['NewImage']['timestamp']['S']

            # Run the data processing
            temp = base64ToValue(encoded_value)
            # Write data to the table
            write_data_to_table(temp, deviceID, timestamp)

        # Ignore REMOVE or MODIFY events
        else:
            print("Event Number: " + str(num) + " (REMOVE)")

    return 'Successfully processed event.'
