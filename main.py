import obd
import time

# INITIAL OBD CONNECTION
port = "/dev/pts/4"
baud = 9600
connection = obd.OBD(port, baud) # Auto-Connect to OBD

# CHANNEL 2

# Get OBD response from specified command
def get_data(command, include_units: bool = False):
    response = connection.query(command)
    
    if not response.is_null():
        value = response.value
        
        if not include_units:
            value = value.magnitude
        
        return value
    
    return None

# OBD COMMANDS
# RPMs
get_rpms = obd.commands.RPM # Command
bound_rpms = 2500 # Switch gear sommand 
bound_rpms_redline = 4500 # REDLINING (Volvo s60)

# Speed
get_speed = obd.commands.SPEED

# Throttle position
get_throttle_pos = obd.commands.THROTTLE_POS

# Engine load - how hard the engine is working
get_engine_load = obd.commands.ENGINE_LOAD

# Coolant temperature - Celsius
get_cool_temp = obd.commands.COOLANT_TEMP
bound_cool_operating = 70
bound_cool_overheat = 105

# Oil temperature - Celsius
get_oil_temp = obd.commands.OIL_TEMP

# Intake air Temperature - Celsius
get_intake_temp = obd.commands.INTAKE_TEMP

# Fuel level
get_fuel_level = obd.commands.FUEL_LEVEL1


while True:
    try:
        # Check for connection
        if not connection.is_connected():
            print("Reconnecting to OBD...")
            connection = obd.OBD(port, baud)
        
        # Get responses
        rpms = get_data(get_rpms, True)
        speed = get_data(get_speed, True)
        throttle_pos = get_data(get_throttle_pos, True)
        engine_load = get_data(get_engine_load, True)
        coolant_temp = get_data(get_cool_temp, True)
        oil_temp = get_data(get_oil_temp, True)
        intake_temp = get_data(get_intake_temp, True)
        fuel_level = get_data(get_fuel_level, True)
        
        
        print(rpms, speed, throttle_pos, engine_load, coolant_temp, oil_temp, intake_temp, fuel_level, sep="\n")

    except Exception as e:
        print(f"Error: {e}")
        connection = obd.OBD(port, baud)
        
    # Cycle 1s
    time.sleep(1)