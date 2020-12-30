# Copyright (c) Microsoft. All rights reserved.
# Licensed under the MIT license. See LICENSE file in the project root for full license information.

import random
import time
import threading
import datetime
from picamera import PiCamera

# Using the Python Device SDK for IoT Hub:
#   https://github.com/Azure/azure-iot-sdk-python
# The sample connects to a device-specific MQTT endpoint on your IoT Hub.
from azure.iot.device import IoTHubDeviceClient, Message, MethodResponse

# The device connection string to authenticate the device with your IoT hub.
# Using the Azure CLI:
# az iot hub device-identity show-connection-string --hub-name {YourIoTHubName} --device-id MyNodeDevice --output table
CONNECTION_STRING = "HostName=iothubbyaugusto.azure-devices.net;DeviceId=device1;SharedAccessKey=bGyzWD5D04IOJDSiRK13tYHizgrMqBFa+MfwEB+eauo=;GatewayHostName=raspberrypi"

# Define the JSON message to send to IoT Hub.
TEMPERATURE = 20.0
HUMIDITY = 60
MSG_TXT = '{{"temperature": {temperature},"humidity": {humidity}}}'

INTERVAL = 5

def iothub_client_init():
    # Create an IoT Hub client
    client = IoTHubDeviceClient.create_from_connection_string(CONNECTION_STRING)
    return client


def device_method_listener(device_client):
    global INTERVAL
    while True:
        method_request = device_client.receive_method_request()
        print (
            "\nMethod callback called with:\nmethodName = {method_name}\npayload = {payload}".format(
                method_name=method_request.name,
                payload=method_request.payload
            )
        )
        if method_request.name == "TakePicture":
            try:
                #payload = method_request.payload
                take_picture()
                send_telemetry(device_client)
            except ValueError:
                response_payload = {"Response": "Invalid parameter"}
                response_status = 400
            else:
                response_payload = {"Response": "Executed direct method {}".format(method_request.name)}
                response_status = 200
        else:
            response_payload = {"Response": "Direct method {} not defined".format(method_request.name)}
            response_status = 404

        method_response = MethodResponse(method_request.request_id, response_status, payload=response_payload)
        device_client.send_method_response(method_response)

def main():
    try:
        # establish device connection
        client = iothub_client_init()

        # Start a thread to listen 
        device_method_thread = threading.Thread(target=device_method_listener, args=(client,))
        device_method_thread.daemon = True
        device_method_thread.start()

        while True:
            time.sleep(10)
            print("alive...")
    except KeyboardInterrupt:
        print ( "IoTHubClient sample stopped" )

def send_telemetry(device_client):

    try:        
        print ( "IoT Hub device sending periodic messages, press Ctrl-C to exit" )
        
        # Build the message with simulated telemetry values.
        temperature = TEMPERATURE + (random.random() * 15)
        humidity = HUMIDITY + (random.random() * 20)
        msg_txt_formatted = MSG_TXT.format(temperature=temperature, humidity=humidity)
        message = Message(msg_txt_formatted)

        # Add a custom application property to the message.
        # An IoT hub can filter on these properties without access to the message body.
        if temperature > 30:
          message.custom_properties["temperatureAlert"] = "true"
        else:
          message.custom_properties["temperatureAlert"] = "false"

        # Send the message.
        print( "Sending message: {}".format(message) )
        device_client.send_message(message)
        print( "Message sent" )
        time.sleep(INTERVAL)

    except Exception as ex:
        print("Exception to send telemetry: %s" % ex)

def take_picture():
        
    try:
        camera = PiCamera()
        camera.rotation = 180

        camera.start_preview()

        time.sleep(2) #warmup the camera
        current_date_and_time = datetime.datetime.now()
        current_date_and_time_string = str(current_date_and_time)
        extension = '.jpg'
        path = '/home/pi/workspace/images/unknown/'
        file_name = path + current_date_and_time_string + extension
        camera.capture(file_name)

        camera.stop_preview()

        print('picture filename: ' + file_name)
        print('\n')
    except Exception as ex:
        print("Exception to take picture: %s" % ex)

if __name__ == '__main__':
    print ( "Press Ctrl-C to exit" )
    main()