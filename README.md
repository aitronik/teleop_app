# teleop_app
[python3.6 or higher required for next steps, ensure that /usr/bin/python3 is a link to /usr/bin/python3.6 or higher. Check this running python3 on terminal, you should see python3.6 version]

REQUIREMEMTS INSTALLATION
 
install kivi :~$sudo apt-get install python3-kivy 

install buildozer :~$pip3 install --user buildozer [if you use a virtualenv, don't use the `--user` option. Ensure that pip3 is for python3.6 or higher]

DEBUG

Go to app root directory and run :~$buildozer android debug 
This will crerate .apk file in ./bin folder

DEPLOY

[Section 1]
1.1 - Enable 'USB debugging' (and 'Install via USB' if present) on device. 
1.2 - Connect Android device to PC with usb cable. 
1.3 - Check if the 'Allow USB debugging' popup appears on device screen.
1.3.1 - If no popup appears skip the following command and go to Section 2
1.3.2 - If permission popup appears, then check 'Allow always on this computer' (optional) and tap OK. 

1.4 - Go to app root directory on PC and run :~$ buildozer android deploy
1.5 - Accept installation on device screen

The .apk file will be installed on your Android device.

[Section 2 - Issues]
If deploy fails or permission has not been required on device screen:
2.1 - install adb :~$ sudo apt install android-sdk-platform-tools
2.2 - follow this guide (https://developer.android.com/studio/run/device) to add user in plugdev group [Not Mandatory: and install android-sdk-platfrom-tools-common for udev rules] 
2.3 - run on terminal :~$ adb devices
you should see 'no permission' next to device id. Try to follow these steps:
2.4 - unplug android device
2.5 - run :~$ adb kill-server
2.6 - run :~$ adb start-server
2.7 - connect android device and check if the 'Allow USB debugging' popup appears on device screen. If it doesn't, skip to 2.11
2.8 - check "Allow always from this computer" option and tap on OK.
2.9 - run :~$ adb devices 
2.10- Now you should see the device id followed by the word 'device', PC has right permission. Hence go to 1.4 [Section 1]
 
2.11- in case of no popup for permission appears, download this repo "https://github.com/M0Rf30/android-udev-rules", 
2.12- got to repo folder and run :~$ sudo cp -v 51-android.rules /etc/udev/rules.d/51-android.rules
2.13- unplug and reconnect android device and 'Allow USB debugging' popup should now appear on device screen. Go back to 1.3.2 [Section 1]

NB. In case of deploy still fails, it might be due to the adb version. Try to download the linux version of Amdroid sdk platform tool from https://androidsdkmanager.azurewebsites.net/Platformtools. Unzip folder and follow steps 1-4 using ./adb instead of adb.

