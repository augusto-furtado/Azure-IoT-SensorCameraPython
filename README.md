SensorCamera
This app take a picture using a camera (OmniVision OV5647 - 5MP) attached to Raspberry PI and send notification to IoT Hub.
The trigger to take a picture is through a direct method call named "TakePicture" or using a Touch Sensor TP223 (this part of the code use the RPi.GPIO lib)

Requirements:
-If connecting to an Azure IoT Edge Gateway, certificate must be installed on Host OS, for linux use:
sudo cp azure-iot-test-only.root.ca.cert.pem /usr/local/share/ca-certificates/azure-iot-test-only.root.ca.cert.pem.crt
sudo update-ca-certificates
-pip3 install azure-iot-device
-pip3 install picamera
-pip install RPi.GPIO


References:
https://github.com/Azure/azure-iot-sdk-python
https://docs.microsoft.com/pt-br/azure/iot-hub/quickstart-send-telemetry-python
https://docs.microsoft.com/pt-br/azure/iot-edge/how-to-connect-downstream-device?view=iotedge-2018-06
https://pypi.org/project/RPi.GPIO/

Tip:
Command to know the expiration of a certificate file:
openssl x509 -enddate -noout -in file.pem