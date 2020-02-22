#!/bin/bash
#-------------------------------------------------------------------------------
# This script installs all requirements needed for an 1.8 inch ST7735 LCD to 
# work with Raspiblitz.
#-------------------------------------------------------------------------------

echo " "
echo "Downloading files required for the library to work..."
echo " "
sudo apt update
sudo apt install build-essential python3-dev python3-smbus python3-pip python3-pil python3-numpy git

echo " "
echo "Installing the Raspberry Pi GPIO and Adafruit GPIO libraries for Python..."
echo " "
sudo python3 -m pip install RPi.GPIO
sudo python3 -m pip install Adafruit_GPIO

# allow the get_btc_sync.sh file to be executable
sudo chmod +x get_btc_sync.sh

echo " "
echo "Cloning the repository and installing the LCD library..."
echo " "
git clone https://github.com/doidotech/DOIDO_Node_LCD.git
cd Python_ST7735
sudo python3 setup.py install

echo " "
echo "Changing /boot/config.tx file to allow use of SPI port..."
echo " "
cd ..
sudo sed -i 's/dtoverlay=tft35a:rotate=270/#dtoverlay=tft35a:rotate=270/g' /boot/config.txt

echo " "
echo "Setup complete!"
echo " "

