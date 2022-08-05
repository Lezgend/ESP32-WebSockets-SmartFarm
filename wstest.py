from MicroWebSrv2 import *
from time         import sleep
from machine      import Pin, Timer
import network, random

# Connecting to WiFi
sta = network.WLAN(network.STA_IF)
if not sta.isconnected():
    print('connecting to network...')
    sta.active(True)
    #sta.connect('your wifi ssid', 'your wifi password')
    sta.connect('SSID', 'PASSWORD')
    while not sta.isconnected():
        pass
print('network config:', sta.ifconfig())

# ============================================================================

# Loads the WebSockets module globally and configure it,
wsMod = MicroWebSrv2.LoadModule('WebSockets')

# Start to setting things up!    
mws2 = MicroWebSrv2()

# For embedded MicroPython, use a very light configuration,
mws2.SetEmbeddedConfig()
mws2._slotsCount = 4

# All pages not found will be redirected to the home '/',
mws2.NotFoundURL = '/'

# Starts the server as easily as possible in managed mode,
mws2.StartManaged()

# ============================================================================

@WebRoute(GET, "/test")
def RequestTestRedirect(microWebSrv2, request):
    content = """
    <!DOCTYPE html>
    <html>
    <head><title>Hello World</title></head>
    <body><p>Hello, World!!!!!</p></body>
    </html>
    """
    print("Received Request")
    request.Response.ReturnOk(content)
    
# ============================================================================

led = Pin(2, Pin.OUT)

relay1 = Pin(15, Pin.OUT)
relay2 = Pin(13, Pin.OUT)
relay3 = Pin(14, Pin.OUT)
relay4 = Pin(12, Pin.OUT)

tm = Timer(0)

def OnTextMessage(webSocket, msg):
    print(f'Received message: {msg} from socket {webSocket}, responding after 1s!')
    LED(webSocket, msg)
    sleep(2)
    webSocket.SendTextMessage("Still working ESP32!")

def OnClosed(webSocket):
    print(f'Websocket {webSocket} closed..')

# MSG Main Function.
def OnWebSocketAccepted(microWebSrv2, webSocket):
    print('New WebSocket accepted from %s:%s.' % webSocket.Request.UserAddress)
    webSocket.OnTextMessage = OnTextMessage
    webSocket.OnClosed = OnClosed
    print(f'Started callbacks on websocket, sending message!')
    webSocket.SendTextMessage("Hi from ESP32!")
    
    cb1 = lambda timer: RealTimeSensor(timer, webSocket)
    tm.init(period=3000, callback=cb1)
    
    
# Reading sensors real time.
def RealTimeSensor(timer, webSocket):

    newtemp = random.randint(0, 50)
    #print(newtemp)
    webSocket.SendTextMessage("temp %s" %newtemp) 
    
    newhumi = random.randint(0, 50)
    #print(newhumi) 
    webSocket.SendTextMessage("humi %s" %newhumi)
    
    newsoil= random.randint(0, 50)
    #print(newsoil) 
    webSocket.SendTextMessage("soil %s" %newsoil)
    
# Waiting relay buttons signal.
def LED(webSocket, msg):
    if msg == "LED_ON1":
        print(msg)
        led.value(1)
        relay1.value(0)
        
    elif msg == "LED_OFF1":
        print(msg)
        led.value(0)
        relay1.value(1)
        
    elif msg == "LED_ON2":
        print(msg)
        relay2.value(0)
        
    elif msg == "LED_OFF2":
        print(msg)
        relay2.value(1)
        
    elif msg == "LED_ON3":
        print(msg)
        relay3.value(0)
        
    elif msg == "LED_OFF3":
        print(msg)
        relay3.value(1)

    elif msg == "LED_ON4":
        print(msg)
        relay4.value(0)
        
    elif msg == "LED_OFF4":
        print(msg)
        relay4.value(1)
        
    else:
        print("Msg: %s" %msg)
        
    webSocket.SendTextMessage("Reply_%s" %msg)

    
wsMod.OnWebSocketAccepted = OnWebSocketAccepted

# ============================================================================

# Main program loop until keyboard interrupt,
try :
    while mws2.IsRunning :
        sleep(1)
except KeyboardInterrupt :
    pass

# End,
mws2.Stop()
print('Bye\n')
