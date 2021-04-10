
import board
import busio
from digitalio import DigitalInOut
import adafruit_esp32spi.adafruit_esp32spi_socket as socket
from adafruit_esp32spi import adafruit_esp32spi
import adafruit_requests as requests

import terminalio
from adafruit_matrixportal.matrix import Matrix
from adafruit_display_text import label

import time


matrix = Matrix()
display = matrix.display

try:
    from secrets import secrets
except ImportError:
    print("WiFi secrets are kept in secrets.py, please add them there!")
    raise

# If you are using a board with pre-defined ESP32 Pins:
esp32_cs = DigitalInOut(board.ESP_CS)
esp32_ready = DigitalInOut(board.ESP_BUSY)
esp32_reset = DigitalInOut(board.ESP_RESET)

spi = busio.SPI(board.SCK, board.MOSI, board.MISO)
esp = adafruit_esp32spi.ESP_SPIcontrol(spi, esp32_cs, esp32_ready, esp32_reset)

while not esp.is_connected:
    try:
        esp.connect_AP(secrets["ssid"], secrets["password"])
    except RuntimeError as e:
        print("could not connect to AP, retrying: ", e)
        continue
print("Connected to", str(esp.ssid, "utf-8"), "\tRSSI:", esp.rssi)

# Initialize a requests object with a socket and esp32spi interface
socket.set_interface(esp)
requests.set_socket(socket, esp)

url = "https://api.kraken.com/0/public/Ticker?pair=adausd"
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.82 Safari/537.36'
    }

prev_price = 0
while True:
    try:
        response = requests.get(url, headers=headers)
        cur_price = response.json()["result"]["ADAUSD"]["c"][0][0:6]
        if float(cur_price) > prev_price:
            # price increase
            text_area = label.Label(terminalio.FONT, text="Cardano \n$"+cur_price, color=0x00FF00)
        elif float(cur_price) < prev_price:
            # price decrease
            text_area = label.Label(terminalio.FONT, text="Cardano \n$"+cur_price, color=0xFF0000)
        else:
            # no price change
            text_area = label.Label(terminalio.FONT, text="Cardano \n$"+cur_price)
        text_area.x = 12
        text_area.y = 7
        display.show(text_area)
        prev_price = float(cur_price)
        time.sleep(10)
    except:
        response.close()

        # Initialize a requests object with a socket and esp32spi interface
        socket.set_interface(esp)
        requests.set_socket(socket, esp)

        text_area = label.Label(terminalio.FONT, text="Getting\n New Price")
        text_area.x = 12
        text_area.y = 7
        display.show(text_area)
        time.sleep(10)
