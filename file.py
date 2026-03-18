# Wireless Communication using Access Point Mode of RPi Pico W

# Libraries
import network
import socket
import time # same as utime library

# Create an Access Point
ssid = 'RPI_PICO_AP'       #Set access point name. you can change this name.
password = '12345678'      #Set your access point password. You can use your own password

ap = network.WLAN(network.AP_IF)
ap.config(essid=ssid, password=password)
ap.active(True)            # Activate the access point

while ap.active() == False:
  pass
print('Connection is successful')
print(ap.ifconfig()) # this line will print the IP address of the Pico board

# Create a socket server
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind(('', 80))
s.listen(5) # maximum number of requests that can be queued

# create a web page
def web_page():
    html = """
<!DOCTYPE html> 
<html> 
<head> 
<title>Pico W Smart Environment Monitor</title> 
<style> 
body{ 
    font-family: Arial; 
    background: linear-gradient(135deg,#0f172a,#1e293b); 
    color:white; 
    text-align:center; 
} 
h1{ 
    margin-top:20px; 
} 
.dashboard{ 
    display:flex; 
    justify-content:center; 
    gap:40px; 
    margin-top:40px; 
} 
.card{
    background:#111827; 
    padding:25px; 
    width:220px; 
    border-radius:15px; 
    box-shadow:0 0 15px rgba(0,0,0,0.6); 
} 
.value{ 
    font-size:40px; 
    margin-top:10px; 
}
.label{ 
    font-size:18px; 
} 
#air{ 
    font-weight:bold; 
}
#alarmBox{ 
    margin-top:40px; 
    padding:20px; 
    font-size:22px; 
    border-radius:10px; 
    width:350px; 
    margin-left:auto; 
    margin-right:auto; 
} 
.safe{ 
    background:#16a34a; 
}
.warning{ 
    background:#eab308; 
}
.danger{ 
    background:#dc2626; 
    animation:flash 1s infinite; 
} 
@keyframes flash{ 
    0%{opacity:1} 
    50%{opacity:.4} 
    100%{opacity:1}
} 
.controls{ 
    margin-top:50px; 
} 
.sliderBox{ 
margin:15px; 
}
</style> 
</head> 
<body> 
<h1>Smart Environmental Monitor</h1> 
<div class="dashboard"> 
<div class="card"> 
<div class="label">Temperature</div> 
<div id="temp" class="value">-- °C</div> 
</div> 
<div class="card"> 
<div class="label">Humidity</div> 
<div id="humidity" class="value">-- %</div> 
</div> 
<div class="card"> 
<div class="label">Air Quality</div> 
<div id="air" class="value">--</div> 
</div> 
</div> 
<div id="alarmBox" class="safe"> 
Air Quality Normal 
</div> 
<div class="controls"> 
<h2>Sensor Simulator</h2> 
<div class="sliderBox"> 
Temperature 
<input type="range" min="0" max="40" value="22" id="tempSlider"> 
</div> 
<div class="sliderBox"> Humidity
<input type="range" min="0" max="100" value="50" id="humSlider"> 
</div>
<div class="sliderBox">
Air Quality 
<input type="range" min="0" max="500" value="100" id="airSlider"> 
</div> 
</div> 
<script> 
const SAFE = 150 
const WARNING = 300
function updateData(){ 
    const temperature = document.getElementById("tempSlider").value 
    const humidity = document.getElementById("humSlider").value 
    const air = document.getElementById("airSlider").value 
    document.getElementById("temp").innerText = temperature + " °C" 
    document.getElementById("humidity").innerText = humidity + " %" 
    document.getElementById("air").innerText = air 
    const alarm = document.getElementById("alarmBox") 
    if(air < SAFE){ 
        alarm.innerText = "Air Quality Good" 
        alarm.className = "safe" 
    } 
    else if(air < WARNING){ 
        alarm.innerText = "Air Quality Moderate" 
        alarm.className = "warning" 
    } 
    else{ 
        alarm.innerText = "⚠ Dangerous Air Quality!" 
        alarm.className = "danger" 
        // send signal to pico alarm 

        // fetch("/alarm?state=on") 
    } 
} 
setInterval(updateData,500) 
</script> 
</body> 
</html>   
            """
    return html


# Response when connection received 
while True:
    conn, addr = s.accept()
    print('Got a connection from %s' % str(addr))
    request = conn.recv(1024)
    response = web_page() # indicate the response when connection is received
    conn.send("HTTP/1.1 200 OK\n")
    conn.send("Content-Type: text/html\n")
    conn.send("Connection: close\n\n")
    conn.sendall(response)
    conn.close()



#     request = str(request)
#     print('Content = %s' % request)
