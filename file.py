import network
import socket
from machine import Pin, ADC
from time import time
import dht
import json

DHT22_Sensor = dht.DHT22(Pin(22))
Gas_Sensor = ADC(Pin(26))
Fire_Alarm = Pin(21, Pin.OUT)

temp = 0
humid = 0
gas = 0
last_read = 0

ssid = 'Pico W Smart Environment Monitor'
password = '12345678'

ap = network.WLAN(network.AP_IF)
ap.config(essid=ssid, password=password)
ap.active(True)

while not ap.active():
    pass

print('AP Ready:', ap.ifconfig())

#Html code
#Async function with a JSON fetch for the data
#If gas value is too large it assumes the sensor has been disconnected
def web_page():
    return """<!DOCTYPE html>
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
.warningText{
    margin-top:10px;
    font-size:16px;
    font-weight:bold;
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
<div class="label">Gas</div> 
<div id="gas" class="value">--</div>
<div id="gasStatus" class="warningText"></div>
</div> 

</div> 

<script>
async function updateData(){ 
    try {
        let res = await fetch("/data");
        let data = await res.json();

        document.getElementById("temp").innerText = data.temp.toFixed(1) + " C";
        document.getElementById("humidity").innerText = data.humid.toFixed(1) + " %";
        document.getElementById("gas").innerText = data.gas;

        let status = "";
        if (data.gas > 10000){
            status = "Gas sensor disconnected. Expect large value";
        } else if (data.gas > 350){
            status = "Excess Smoke. Triggering Fire Alarm";
        } else if (data.gas > 150){
            status = "Excess CO2";
        } else {
            status = "Air Quality Normal";
        }

        document.getElementById("gasStatus").innerText = status;

    } catch(e) {
        console.log("Error:", e);
    }
}

setInterval(updateData, 2000);
updateData();
</script> 

</body> 
</html>"""
    

#Waiting for someone to connect

addr = socket.getaddrinfo('0.0.0.0', 80)[0][-1]
s = socket.socket()
s.bind(addr)
s.listen(1)

print("Server running")


while True:
    try:
        # Esnures it refreshes every 2 seconds and no less otherwise DHT22 sensor will error
        if time() - last_read > 2:
            try:
                DHT22_Sensor.measure()
                gas = Gas_Sensor.read_u16() 
                temp = DHT22_Sensor.temperature()
                humid = DHT22_Sensor.humidity()
                print("Updated:", temp, humid, gas)
                
                if gas > 350:
                    Fire_Alarm.on()
                else:
                    Fire_Alarm.off()
            except:
                print("Sensor error")
            last_read = time()

        conn, addr = s.accept()
        request = conn.recv(1024).decode()

        # Responds the the fetch, packages up the data and sends it
        if "/data" in request:
            data = json.dumps({
                "temp": temp,
                "humid": humid,
                "gas" : gas
            })


            conn.send(b'HTTP/1.1 200 OK\r\nContent-Type: application/json\r\n\r\n')
            conn.sendall(data.encode())

        else:
            #Dont send data if not requested
            conn.send(b'HTTP/1.1 200 OK\r\nContent-Type: text/html\r\n\r\n')
            conn.sendall(web_page().encode())

        conn.close()

    except Exception as e:
        print("Error:", e)
        try:
            conn.close()
        except:
            pass
