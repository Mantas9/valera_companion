import obd
import time

# INITIAL OBD CONNECTION
port = "/dev/rfcomm0"
baud = 9600
connection = obd.OBD(port, baud) # Auto-Connect to OBD

# CHANNEL 2

# OBD COMMANDS
get_rpms = obd.commands.RPM 
get_oil_temp = obd.commands.OIL_TEMP



while True:
    try:
        if not connection.is_connected():
            print("Reconnecting to OBD...")
            connection = obd.OBD(port, baud)
        
        response = connection.query(get_rpms)

        if not response.is_null():
            rpm = response.value.to("rpm").magnitude
            print(f"RPM: {rpm}")
            if rpm >= 2000:
                print("Shift gears")
        else:
            print("No RPM data")

    except Exception as e:
        print(f"Error: {e}")
        connection = obd.OBD(port, baud)
        
    # Cycle 1s
    time.sleep(1)