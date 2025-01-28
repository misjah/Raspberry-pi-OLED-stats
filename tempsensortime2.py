import time
import subprocess
from datetime import datetime
from luma.core.interface.serial import i2c
from luma.core.render import canvas
from luma.oled.device import sh1106, ssd1306
from PIL import ImageFont, ImageDraw, Image
from w1thermsensor import W1ThermSensor

serial = i2c(port=1, address=0x3C)
device = sh1106(serial)

#oled_font = ImageFont.truetype("DejaVuSerif.ttf", 14)
oled_font = ImageFont.load_default()

sensor = W1ThermSensor()

while True:
    cmd = "hostname -I | cut -d\' \' -f1 | awk '{printf \"IP: %s\", $0}'"
    IP = subprocess.check_output(cmd, shell=True)
    cmd = "top -bn1 | grep load | awk '{printf \"CPU Load: %.2f\", $(NF-2)*100/4}'"
    CPU = subprocess.check_output(cmd, shell=True).decode().strip() + '%'
    cmd = "free -m | awk 'NR==2{printf \"MEM:%s/%sMB %.2f%%\", $3,$2,$3*100/$2 }'"
    MemUsage = subprocess.check_output(cmd, shell=True)
    cmd = "df -h | awk '$NF==\"/\"{printf \"Disk: %d/%dGB %s\", $3,$2,$5}'"
    Disk = subprocess.check_output(cmd, shell=True)
    Temp = "AUX: {:.1f}C".format(sensor.get_temperature())
    cpu_temp = subprocess.check_output("vcgencmd measure_temp | cut -d'=' -f2", shell=True).decode().strip()
    cpu_temp = float(cpu_temp.replace("'C", ""))
    CPUTemp = "CPU: {:.1f}C".format(cpu_temp)
    cmd = "grep eth0 /proc/net/dev | awk '{printf \"RX/TX: %.2f/%.2f MB\",($2/1000000),($10/1000000)}'"
    Network = subprocess.check_output(cmd, shell=True)

    now = datetime.now()
    current_time = now.strftime("%I:%M:%S%p").lower().replace('am', 'a').replace('pm', 'p')
    current_date = now.strftime("%d.%m.%Y")

    with canvas(device, dither=True) as draw:
        #draw.rectangle(device.bounding_box, outline = "white", fill = "black")
        draw.text((0, 0),  IP, font=oled_font, fill="white")
        draw.text((0, 8), CPU, font=oled_font, fill="white")
        draw.text((0, 17), MemUsage, font=oled_font, fill="white")
        draw.text((0, 26), Disk, font=oled_font, fill="white")
        draw.text((0, 35), CPUTemp + " " + Temp, font=oled_font, fill="white")
        draw.text((0, 44), Network, font=oled_font, fill="white")
        draw.text((0, 53), current_time + " " + current_date, font=oled_font, fill="white")
        
        #draw.text((60, 60), current_date, font=oled_font, fill="white")

    time.sleep(.1)
