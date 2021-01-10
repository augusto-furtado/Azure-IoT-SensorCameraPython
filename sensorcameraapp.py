# Copyright (c) Microsoft. All rights reserved.
# Licensed under the MIT license. See LICENSE file in the project root for full license information.

import random
import time
import threading
import datetime
import os
import RPi.GPIO as GPIO
from picamera import PiCamera
from azure.iot.device import IoTHubDeviceClient, Message, MethodResponse

# The device connection string to authenticate the device with your IoT hub.
CONNECTION_STRING = "HostName=iothubbyaugusto.azure-devices.net;DeviceId=device1;SharedAccessKey=bGyzWD5D04IOJDSiRK13tYHizgrMqBFa+MfwEB+eauo=;GatewayHostName=raspberrypi"
camera_instance = PiCamera()

def iothub_client_init():
    # Create an IoT Hub client
    client = IoTHubDeviceClient.create_from_connection_string(CONNECTION_STRING)
    return client

def device_method_listener(device_client):
    while True:
        method_request = device_client.receive_method_request()
        
        if method_request.name == "TakePicture":
            try:
                #Example how to read the payload content
                #payload = method_request.payload
                
                take_picture(camera_instance)
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
        iothub_client = iothub_client_init()

        #set gpio pin for touch sensor
        gpio_touch_sensor = 17

        # set camera properties
        camera_instance.rotation = 180

        # Start a thread to listen iot hub direct method call
        device_method_thread = threading.Thread(target=device_method_listener, args=(iothub_client,))
        device_method_thread.daemon = True
        device_method_thread.start()

        # Start a thread to listen touch sensor 
        touch_sensor_thread = threading.Thread(target=touch_sensor_listener, args=(iothub_client, gpio_touch_sensor,))
        touch_sensor_thread.daemon = True
        touch_sensor_thread.start()

        while True:
            time.sleep(10)
            print(".")
    except KeyboardInterrupt:
        print ( "App stopped" )

def touch_sensor_listener(device_client, gpio_pin):
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(gpio_pin, GPIO.IN,pull_up_down=GPIO.PUD_UP)

    while True:
        if (GPIO.input(gpio_pin) == True):
            print ('pressed')
            try:
                take_picture(camera_instance)
                send_telemetry(device_client)
            except Exception as ex:
                print("Exception: %s" % ex) 
        time.sleep(2)

def send_telemetry(device_client):

    try:        
        # Build the message with simulated telemetry values.
        
        # Example to send payload using json format
        #MSG_TXT = '{{"temperature": {temperature},"humidity": {humidity}}}'
        #temperature = TEMPERATURE + (random.random() * 15)
        #humidity = HUMIDITY + (random.random() * 20)
        #msg_txt_formatted = MSG_TXT.format(temperature=temperature, humidity=humidity)
        #message = Message(msg_txt_formatted)

        #Send payload as a simple text
        message = Message("newImage")

        # Add a custom application property to the message.
        message.custom_properties["source"] = "edgeRaspberryPI"
        
        # Send the message.
        device_client.send_message(message)
        print( "Message sent" )
        
    except Exception as ex:
        print("Exception to send telemetry: %s" % ex)

def take_picture(camera_instance):
        
    try:        
        camera_instance.start_preview()

        time.sleep(2) #warmup the camera
        current_date_and_time = datetime.datetime.now()
        current_date_and_time_string = str(current_date_and_time)
        extension = '.jpg'
        path = '/home/pi/workspace/images/unknown/'
        file_name = path + current_date_and_time_string + extension
        camera_instance.capture(file_name)

        camera_instance.stop_preview()

        print('picture filename: ' + file_name)
        print('\n')
    except Exception as ex:
        print("Exception to take picture: %s" % ex)

if __name__ == '__main__':
    print ( "Press Ctrl-C to exit" )
    main()