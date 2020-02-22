#MyNodeLCD_V1.0.py
#-------------------------------------------------------------------------------
# This software displays scraped MyNode data on an 1.8 inch ST7735 display.
# The data is scraped from a mynode webserver html page.
#-------------------------------------------------------------------------------

from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont
import time

import ST7735 as TFT
import Adafruit_GPIO as GPIO
import Adafruit_GPIO.SPI as SPI

import urllib.request
import json
import socket

# For data scraping
from lxml import html
import requests
import re
import datetime
import sys 


WIDTH = 128
HEIGHT = 160
SPEED_HZ = 4000000


# Raspberry Pi configuration.
DC = 24
RST = 25
SPI_PORT = 0
SPI_DEVICE = 0

# Create TFT LCD display class.
disp = TFT.ST7735(
    DC,
    rst=RST,
    spi=SPI.SpiDev(
        SPI_PORT,
        SPI_DEVICE,
        max_speed_hz=SPEED_HZ))

# Initialize display.
disp.begin()

# Clear display, white background
disp.clear((255, 255, 255))
disp.display()

# Get a PIL Draw object to start drawing on the display buffer.
draw = disp.draw()

# Create login session object
s = requests.Session()
LOGIN = 'http://mynode.local/login'
new_password = sys.argv[1]
login_payload = {
        'username': 'mynode',
        'password': new_password
    }
s.post(LOGIN, data=login_payload)

# customizable images path
images_path = '/var/www/mynode/static/images/'

# Define a function to initialize the display.
def initialize__lcd():
    # Initialize display.
    disp.begin()

    #Clear display, white background
    disp.clear((255, 255, 255))
    
    disp.display()
    
# Define a function to calculate an inverted x co-ordinate.
def get_inverted_x(currentX, objectSize):
    invertedX = WIDTH - (currentX + objectSize)
    return invertedX


# Define a function to draw a logo on display
def display_logo(image, image_path, position):
    # Load an image.
    picimage = Image.open(image_path)
    # Convert to RGBA
    picimage = picimage.convert('RGBA')
    # Resize the image
    picimage = picimage.resize((80, 19), Image.BICUBIC)
    # Rotate image
    rotated = picimage.rotate(270, expand=1)
    # Paste the image into the screen buffer
    image.paste(rotated, position, rotated)
    
# Define a function to draw an enabled service icon.
def display_service_icon(image, image_path, position):
    # Load an image.
    picimage = Image.open(image_path)
    # Convert to RGBA
    picimage = picimage.convert('RGBA')
    # Resize the image
    picimage = picimage.resize((26, 26), Image.BICUBIC)
    # Rotate image
    rotated = picimage.rotate(270, expand=1)
    # Paste the image into the screen buffer
    image.paste(rotated, position, rotated)

# Define a function to draw myNode logo without parameters
def display_mynode_logo():
    # Draw logo 
    display_logo(disp.buffer, images_path+'logo.png', (get_inverted_x(10, 19), int((160-80)/2)))
    

    
# Define a function to create centered justified text.
def draw_centered_text(image, text, xposition, angle, font, fill=(255,255,255)):
    # Get rendered font width and height.
    draw = ImageDraw.Draw(image)
    width, height = draw.textsize(text, font=font)
    # Create a new image with transparent background to store the text.
    textimage = Image.new('RGBA', (width, height), (0,0,0,0))
    # Render the text.
    textdraw = ImageDraw.Draw(textimage)
    textdraw.text((0,0), text, font=font, fill=fill)
    W, H = (128,160)
    # Rotate the text image.
    rotated = textimage.rotate(angle, expand=1)
    # Paste the text into the image, using it as a mask for transparency.
    xCordinate = xposition
    yCordinate = int((H-width)/2)
    
    image.paste(rotated, (xCordinate,yCordinate), rotated)
    
# Define a function to create rotated text.
def draw_rotated_text(image, text, position, angle, font, fill=(255,255,255)):
    # Get rendered font width and height.
    draw = ImageDraw.Draw(image)
    width, height = draw.textsize(text, font=font)
    # Create a new image with transparent background to store the text.
    textimage = Image.new('RGBA', (width, height), (0,0,0,0))
    # Render the text.
    textdraw = ImageDraw.Draw(textimage)
    textdraw.text((0,0), text, font=font, fill=fill)
    # Rotate the text image.
    rotated = textimage.rotate(angle, expand=1)
    # Paste the text into the image, using it as a mask for transparency.
    image.paste(rotated, position, rotated)

# Define a function to find a word using regex
def findWholeWord(w):
    return re.compile(r'\b({0})\b'.format(w), flags=re.IGNORECASE).search
# Define a function to return a word search result
def get_search_result(word,sentence):
    match_object = findWholeWord(word)(sentence)
    
    if match_object == None:
        return False
    else:
        return True
    
# Define a function to draw staring scene.
def draw_starting_scene():
    display_mynode_logo()
    font20 = ImageFont.truetype("/usr/share/fonts/truetype/lato/Lato-Medium.ttf", 20)
    font13 = ImageFont.truetype("/usr/share/fonts/truetype/lato/Lato-Medium.ttf", 13)
    draw_centered_text(disp.buffer, "Starting...", get_inverted_x(40, 20), 270, font20, fill=(0,0,0))
    draw_centered_text(disp.buffer, "Launching myNode ", get_inverted_x(65, 13), 270, font13, fill=(0,0,0))
    draw_centered_text(disp.buffer, "services...", get_inverted_x(83, 13), 270, font13, fill=(0,0,0))
    #disp.display()
    
# Define looking for drive scene.
def draw_looking_for_drive_scene():
    display_mynode_logo()
    font20 = ImageFont.truetype("/usr/share/fonts/truetype/lato/Lato-Medium.ttf", 20)
    font13 = ImageFont.truetype("/usr/share/fonts/truetype/lato/Lato-Medium.ttf", 13)
    draw_centered_text(disp.buffer, "Looking for Drive", get_inverted_x(40, 20), 270, font20, fill=(0,0,0))
    draw_centered_text(disp.buffer, "Please attach a drive", get_inverted_x(65, 13), 270, font13, fill=(0,0,0))
    draw_centered_text(disp.buffer, "to your myNode", get_inverted_x(83, 13), 270, font13, fill=(0,0,0))
    #disp.display()
    
# Define a function to draw downloading scene.
def draw_downloading_scene(newComplete, new_dl_rate):
    display_mynode_logo()
    font20 = ImageFont.truetype("/usr/share/fonts/truetype/lato/Lato-Medium.ttf", 20)
    font13 = ImageFont.truetype("/usr/share/fonts/truetype/lato/Lato-Medium.ttf", 13)
    draw_centered_text(disp.buffer, "QuickSync", get_inverted_x(40, 20), 270, font20, fill=(0,0,0))
    draw_centered_text(disp.buffer, "Downloading...", get_inverted_x(65, 13), 270, font13, fill=(0,0,0))
    draw_centered_text(disp.buffer, newComplete, get_inverted_x(83, 13), 270, font13, fill=(0,0,0))
    draw_centered_text(disp.buffer, new_dl_rate, get_inverted_x(101, 13), 270, font13, fill=(0,0,0))
    #disp.display()
    
# Define a function to draw waiting for download scene.
def draw_wait_download_scene():
    display_mynode_logo()
    font20 = ImageFont.truetype("/usr/share/fonts/truetype/lato/Lato-Medium.ttf", 20)
    font13 = ImageFont.truetype("/usr/share/fonts/truetype/lato/Lato-Medium.ttf", 13)
    draw_centered_text(disp.buffer, "QuickSync", get_inverted_x(40, 20), 270, font20, fill=(0,0,0))
    draw_centered_text(disp.buffer, "Starting", get_inverted_x(65, 13), 270, font13, fill=(0,0,0))
    draw_centered_text(disp.buffer, "Waiting on download client ", get_inverted_x(83, 13), 270, font13, fill=(0,0,0))
    draw_centered_text(disp.buffer, "to start...", get_inverted_x(101, 13), 270, font13, fill=(0,0,0))
    #disp.display()

    
# Define a function to draw copying scene.
def draw_copying_scene(newPercent):
    display_mynode_logo()
    font20 = ImageFont.truetype("/usr/share/fonts/truetype/lato/Lato-Medium.ttf", 20)
    font13 = ImageFont.truetype("/usr/share/fonts/truetype/lato/Lato-Medium.ttf", 13)
    draw_centered_text(disp.buffer, "QuickSync", get_inverted_x(40, 20), 270, font20, fill=(0,0,0))
    draw_centered_text(disp.buffer, "Copying files...", get_inverted_x(65, 13), 270, font13, fill=(0,0,0))
    draw_centered_text(disp.buffer, "This will take several hours", get_inverted_x(83, 13), 270, font13, fill=(0,0,0))
    draw_centered_text(disp.buffer, newPercent, get_inverted_x(101, 13), 270, font13, fill=(0,0,0))
    #disp.display()
    
# Define a function to draw syncing scene.
def draw_syncing_scene(new_sync_state):
    display_mynode_logo()
    font19 = ImageFont.truetype("/usr/share/fonts/truetype/lato/Lato-Medium.ttf", 19)
    font13 = ImageFont.truetype("/usr/share/fonts/truetype/lato/Lato-Medium.ttf", 13)
    draw_centered_text(disp.buffer, "Bitcoin Blockchain", get_inverted_x(45, 19), 270, font19, fill=(0,0,0))
    draw_centered_text(disp.buffer, "Syncing...", get_inverted_x(70, 13), 270, font13, fill=(0,0,0))
    draw_centered_text(disp.buffer, new_sync_state, get_inverted_x(88, 13), 270, font13, fill=(0,0,0))
    #disp.display()
    
# Define a function to get an icon display location.
def get_icon_position(iconNumber):
    if iconNumber == 1:
        return (get_inverted_x(55, 26), 5)
    elif iconNumber == 2:
        return (get_inverted_x(55, 26), 36)
    elif iconNumber == 3:
        return (get_inverted_x(55, 26), 67)
    elif iconNumber == 4:
        return (get_inverted_x(55, 26), 98)
    elif iconNumber == 5:
        return (get_inverted_x(55, 26), 129)
    elif iconNumber == 6:
        return (get_inverted_x(86, 26), 5)
    elif iconNumber == 7:
        return (get_inverted_x(86, 26), 36)
    elif iconNumber == 8:
        return (get_inverted_x(86, 26), 67)
    elif iconNumber == 9:
        return (get_inverted_x(86, 26), 98)
    elif iconNumber == 10:
        return (get_inverted_x(86, 26), 129)
    
# Define a function to draw services scene.
def draw_services_scene(new_bitcoind_status_color, new_lnd_status_color,new_electrs_status_color,new_vpn_status_color,new_rtl_status_color,
                        new_explorer_status_color,new_lnd_admin_status_color,new_lnd_connect_status_color,new_lndhub_status_color,new_tor_services_status_color,new_device_temp,
                        new_bitcoind_synced_color):
    font20 = ImageFont.truetype("/usr/share/fonts/truetype/lato/Lato-Medium.ttf", 20)
    font11 = ImageFont.truetype("/usr/share/fonts/truetype/lato/Lato-Medium.ttf", 11)
    
    # Display current bitcoin price
    try:
        url = "https://min-api.cryptocompare.com/data/price?fsym=BTC&tsyms=KES,USD"
        currentPrice = urllib.request.urlopen(url).read()
        price_dict = json.loads(currentPrice)
        #price = str(7355.17)
        price = str(int(price_dict['USD']))
        #print("BTC: $" + price)
        priceXPosition = 30
        disp.clear((255, 255, 255))
        draw_centered_text(disp.buffer, "$ "+price, get_inverted_x(30, 20), 270, font20, fill=(255,0,0))
    except:
        disp.clear((255, 255, 255))
        draw_centered_text(disp.buffer, "$ ", get_inverted_x(30, 20), 270, font20, fill=(255,0,0))
    if get_search_result("green",new_bitcoind_synced_color):
        display_mynode_logo()
    else:
        display_mynode_logo()
    
    # Display enabled service icons
    iconNum = 0
    
    if get_search_result("green",new_bitcoind_status_color):
        iconNum = iconNum +1
        display_service_icon(disp.buffer, images_path+'bitcoin.png', get_icon_position(iconNum))
        
    if get_search_result("green",new_lnd_status_color):
        iconNum = iconNum +1
        display_service_icon(disp.buffer, images_path+'lightning.png', get_icon_position(iconNum))
        
    if get_search_result("green",new_electrs_status_color):
        iconNum = iconNum +1
        display_service_icon(disp.buffer, images_path+'electrum_logo.png', get_icon_position(iconNum))
        
    if get_search_result("green",new_vpn_status_color):
        iconNum = iconNum +1
        display_service_icon(disp.buffer, images_path+'vpn.png', get_icon_position(iconNum))
        
    if get_search_result("green",new_rtl_status_color):
        iconNum = iconNum +1
        display_service_icon(disp.buffer, images_path+'rtl.png', get_icon_position(iconNum))
    
    if get_search_result("green",new_explorer_status_color):
        iconNum = iconNum +1
        display_service_icon(disp.buffer, images_path+'bitcoin.png', get_icon_position(iconNum))
        
    if get_search_result("green",new_lnd_admin_status_color):
        iconNum = iconNum +1
        display_service_icon(disp.buffer, images_path+'lnd_admin.png', get_icon_position(iconNum))
    
    if get_search_result("green",new_lnd_connect_status_color):
        iconNum = iconNum +1
        display_service_icon(disp.buffer, images_path+'lndconnect.png', get_icon_position(iconNum))
    
    if get_search_result("green",new_lndhub_status_color):
        iconNum = iconNum +1
        display_service_icon(disp.buffer, images_path+'lndhub.png', get_icon_position(iconNum))
     
    if get_search_result("green",new_tor_services_status_color):
        iconNum = iconNum +1
        display_service_icon(disp.buffer, images_path+'tor.png', get_icon_position(iconNum))
    
    # Display temperature
    draw_rotated_text(disp.buffer, new_device_temp, (3, HEIGHT-30), 270, font11, fill=(0,0,0))
    # Do the display now
    #disp.display()
 

# Define a function to create a session with server
def create_session():
    PROTECTED_PAGE = 'http://mynode.local/'
    response = s.get(PROTECTED_PAGE)
    #print(response.text)
    return response
    
# Define a function to display home page data
def display_home_page(app_status_list, temperature_list):
    
    # If list has items
    if app_status_list:
        # Set colors to empty first
        bitcoin_color = ""       
        lightning_color = ""       
        electrum_server_color = ""    
        vpn_color = ""     
        rtl_color = ""      
        lnd_admin_color = ""    
        lnd_connect_color = ""    
        lnd_hub_color = "" 
        btc_explorer_color = "" 
        btc_rpc_explorer_color = "" 
        tor_services_color = "" 
        btc_cli_color = "" 
        
        for dict_el in app_status_list:
            newDict = dict_el
            appTitle = newDict["app_title"]
            appColor = newDict["app_status_icon"]
            appStatus = newDict["app_status"]
            
            if appTitle == "Bitcoin":
                bitcoin_color = appColor
            elif appTitle == "Lightning":
                lightning_color = appColor
            elif appTitle == "Electrum Server":
                electrum_server_color = appColor
            elif appTitle == "VPN":
                vpn_color = appColor
            elif appTitle == "RTL":
                rtl_color = appColor
            elif appTitle == "LND Admin":
                lnd_admin_color = appColor
            elif appTitle == "LND Connect":
                lnd_connect_color = appColor
            elif appTitle == "LND Hub":
                lnd_hub_color = appColor
            elif appTitle == "Explorer" and appStatus == "BTC RPC Explorer":
                btc_rpc_explorer_color = appColor
            elif appTitle == "Explorer":
                btc_explorer_color = appColor
            elif appTitle == "Tor Services":
                tor_services_color = appColor
            elif appTitle == "BTC CLI":
                btc_cli_color = appColor

        # Get temperature now
        temp_list_len = len(temperature_list)
        #print("temperature list len: ", temp_list_len)
        # Expect 4 items in list
        if temp_list_len == 4:
            device_temperature = temperature_list[3]
            # We have all data, draw the services scene now
            draw_services_scene(bitcoin_color, lightning_color,electrum_server_color,vpn_color,rtl_color,btc_explorer_color,lnd_admin_color,lnd_connect_color,lnd_hub_color,tor_services_color,device_temperature,lightning_color)
    
#define a function to get and display data
def get_display_data():
    # Get the html page
    page = create_session()
    tree = html.fromstring(page.content)

    #This will get the state header:
    state_header_list = tree.xpath('//div[@class="state_header"]/text()')
    #This will get the state subheader
    state_subheader_list = tree.xpath('//div[@class="state_subheader"]/text()')
    # This will get subheader text after <br> tag
    state_subheader_list2 = tree.xpath('//div[@class="state_subheader"]/text()[preceding-sibling::br]')
    # This will get the page title
    page_title_list = tree.xpath('//title/text()')
    # This will get temperature data
    temperature_list = tree.xpath('//div[@class="drive_usage"]/text()')
    # This will get the services status color
    app_status_icon_list = tree.xpath("//div[@class='app_tile']")
    # A list to hold a dictionary for each icon
    app_icons_list = []
    for el in app_status_icon_list:
        # This gets the status color
        el_temp = el.xpath(".//div[contains(@class,'app_status_icon')]")
        app_status_color_icon_list = el_temp[0].xpath('@class')
        # This gets the app title
        app_title_list = el.xpath(".//div[contains(@class,'app_title')]/text()")
        # This gets the app status
        app_status_list = el.xpath(".//div[contains(@class,'app_status')]/text()")
        
        if app_status_color_icon_list:
            app_status_icon = app_status_color_icon_list[0]
        else:
            app_status_icon = ""
        if app_title_list:
            app_title = app_title_list[0]
        else:
            app_title = ""
        if app_status_list:
            app_status = app_status_list[0]
        else:
            app_status = ""
            
        newDict={"app_status_icon":app_status_icon, "app_title":app_title, "app_status":app_status}
        #print(newDict)
        app_icons_list.append(newDict)
    #print("App dictionary list: ",app_icons_list)

    # Check if lists are empty first
    if state_header_list:
        state_header = state_header_list[0]
    else:
        state_header = ""
        
    if state_subheader_list:
        state_subheader = state_subheader_list[0]
    else:
        state_subheader = ""
        
    # Get the text after the <br> tag
    if state_subheader_list2:
        state_subheader2 = state_subheader_list2[0]
    else:
        state_subheader2 = ""
    
    if page_title_list:
        page_title = page_title_list[0]
    else:
        page_title = ""

    # Check state of mynode and display
    
    # Device is starting
    if state_header == "Starting...":
        disp.clear((255, 255, 255))
        draw_starting_scene()
        
    # Device is looking for hard drive
    elif state_header == "Looking for Drive":
        disp.clear((255, 255, 255))
        draw_looking_for_drive_scene()
             
    # Device is waiting for dowload
    elif get_search_result("Starting",state_subheader):
        disp.clear((255, 255, 255))
        draw_wait_download_scene()
        
    # Device is downloading
    elif get_search_result("Downloading",state_subheader):
        subheader_data_array = state_subheader2.split('%')
        complete = subheader_data_array[0]+"%"
        dl_rate = subheader_data_array[1]
        disp.clear((255, 255, 255))
        draw_downloading_scene(complete, dl_rate)
        
    # Device is copying files
    elif get_search_result("Copying",state_subheader):
        percent = state_subheader2
        disp.clear((255, 255, 255))
        draw_copying_scene(percent)
        
    # Device is syncing
    elif get_search_result("Syncing",state_subheader):
        sync_state = state_subheader2
        disp.clear((255, 255, 255))
        draw_syncing_scene(sync_state)
        
    # Device is stable (homepage)
    elif page_title == "myNode Home":
        display_home_page(app_icons_list,temperature_list)
        
    
    
# Draw the image on the display hardware.
print('Entering loop')
# Display the four scenes in a loop
while True:
    # Get display data
    #disp.clear((255, 255, 255))
    #print(datetime.datetime.now())
    try:
        get_display_data()
        #print(datetime.datetime.now())
    except:
        print("error")
        font20 = ImageFont.truetype("/usr/share/fonts/truetype/lato/Lato-Medium.ttf", 20)
        disp.clear((255, 255, 255))
        draw_centered_text(disp.buffer, "ERROR!", get_inverted_x(30, 20), 270, font20, fill=(255,0,0))
        
    #get_display_data()
    # Refresh display and wait
    disp.display()
    time.sleep(60)



