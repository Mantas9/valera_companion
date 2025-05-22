import obd
import time

# INITIAL OBD CONNECTION
port = "/dev/pts/4"
baud = 9600
connection = obd.OBD(port, baud) # Auto-Connect to OBD

# REAL LIFE OBD USES BLUETOOTH CHANNEL 2!!!

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
speed_last = -1 # Speed last second
speed_veryfast = 140 # Kerosene on 140 km/h


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
get_fuel_level = obd.commands.FUEL_LEVEL
fuel_low = 15 # Percent
fuel_remind_interval = 1800 # Seconds, 1800s - 30min

# Air flow rate (MAF)
get_maf = obd.commands.MAF

# Fuel rate
get_fuel_rate = obd.commands.FUEL_RATE


while True:
    try:
        # Check for connection
        if not connection.is_connected():
            print("Reconnecting to OBD...")
            connection = obd.OBD(port, baud)
        
        # Get responses
        rpms = get_data(get_rpms)
        speed = get_data(get_speed)
        throttle_pos = get_data(get_throttle_pos)
        engine_load = get_data(get_engine_load)
        coolant_temp = get_data(get_cool_temp)
        oil_temp = get_data(get_oil_temp)
        intake_temp = get_data(get_intake_temp)
        fuel_level = get_data(get_fuel_level)
        
        
        
        
        print(rpms, speed, throttle_pos, engine_load, coolant_temp, oil_temp, intake_temp, fuel_level, speed_last, sep="\n")
        
        # Set speed to be last second speed at the end
        speed_last = float(speed)

    except Exception as e:
        print(f"Error: {e}")
        connection = obd.OBD(port, baud)
        
    # Cycle 1s
    time.sleep(1)