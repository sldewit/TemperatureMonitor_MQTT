from pi1wire import Pi1Wire, Resolution

#for s in Pi1Wire().find_all_sensors():
#    print(f'{s.mac_address} = {s.get_temperature():.3f}')
try:
    Temp1 = Pi1Wire().find("28dfc6571f64ff")
except:
    print("T1 not found")

try:
    Temp2 = Pi1Wire().find("28dfd9571f64ff")
except:
    print("T2 not found")

while True:   
    try:
        print("T1=")
        print(f'{Temp1.get_temperature():.3f}')
    except:
        print("T1 not found")
    try:    
        print("T2=")
        print(f'{Temp2.get_temperature():.3f}')
    except:
        print("T2 not found")
