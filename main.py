import obd
import time

# INITIAL OBD CONNECTION
port = "/dev/pts/4"
baud = 9600
connection = obd.OBD(port, baud) # Auto-Connect to OBD

# CHANNEL 2

# Get OBD response from specified command
def get_data(command):
    response = connection.query(command)
    
    if not response.is_null():
        value = response.value.magnitude
        return value
    
    return None

# OBD COMMANDS
# RPMs
get_rpms = obd.commands.RPM # Command
bound_rpms = 2500 # Switch gear sommand 
bound_rpms_redline = 4500 # REDLINING (Volvo s60)

# Coolant Temperature - Celsius
get_cool_temp = obd.commands.COOLANT_TEMP
bound_cool_operating = 70
bound_cool_overheat = 105


while True:
    try:
        # Check for connection
        if not connection.is_connected():
            print("Reconnecting to OBD...")
            connection = obd.OBD(port, baud)
        
        # Get responses
        rpms = get_data(get_rpms)
        coolant = get_data(get_cool_temp)
        
        print(rpms, coolant)

    except Exception as e:
        print(f"Error: {e}")
        connection = obd.OBD(port, baud)
        
    # Cycle 1s
    time.sleep(1)