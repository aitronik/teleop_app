# teleop_app
**[python3.6 or higher required for next steps, ensure that /usr/bin/python3 is a link to /usr/bin/python3.6 or higher. Check this running python3 on terminal, you should see python3.6 version activated]**

## REQUIREMEMTS INSTALLATION
 
install kivi: `sudo apt-get install python3-kivy`

install buildozer: `pip3 install --user buildozer`

## DEBUG

Go to app root directory and run: `buildozer android debug`

This will create .apk file in ./bin folder

## DEPLOY

### Section 1
1.1 Enable "_USB debugging_" (and "_Install via USB_" if present) on device. 

1.2 Connect Android device to PC with USB cable. 

1.3 Check if the "_Allow USB debugging_" popup appears on device screen. If no popup appears go to Section 2

1.4 If permission popup appears, then select "_Allow always on this computer_" (optional) and tap OK. 

1.5 Go to app root directory on PC and run: `buildozer android deploy`

1.6 Accept installation on device screen

The .apk file will be installed on your Android device.

### Section 2 - Issues

If deploy fails or permission popup does not appears on device screen:

2.1 Install adb: `sudo apt install android-sdk-platform-tools`

2.2 Follow (https://developer.android.com/studio/run/device) to add user in plugdev group and install _android-sdk-platfrom-tools-common_ for udev rules

2.3 Run: `adb devices`

You should see '_no permission_' next to device id. Try to follow these steps:

2.4 Unplug Android device

2.5 Run: `adb kill-server`

2.6 Run: `adb start-server`

2.7 Connect Android device and check if the "_Allow USB debugging_" popup appears on device screen. If it doesn't, skip to 2.11

2.8 Check "_Allow always from this computer_" option and tap OK.

2.9 Run: `adb devices`

2.10 Now you should see the device id followed by the word '_device_'; PC has right permission. Hence go to 1.4 [Section 1]
 
2.11 In case of popup for permission does not appear, download this repo (https://github.com/M0Rf30/android-udev-rules) to add an Android rule

2.12 Go to repo folder and run: `sudo cp -v 51-android.rules /etc/udev/rules.d/51-android.rules`

2.13 Unplug and reconnect Android device, thus "_Allow USB debugging_" popup should now appear on device screen. Go back to 1.3.2 [Section 1]

NB. In case of deploy still fails, it might be due to the adb version. Try to download the linux version of Android sdk platform tool from (https://androidsdkmanager.azurewebsites.net/Platformtools), unzip folder and follow steps 2.4 - 2.8 using `./adb` instead of `adb`.

