import obd
import time
import pygame
import random
from pathlib import Path

# ========== OBD CONNECTION BASICS
port = "/dev/pts/4"
baud = 9600
connection = obd.OBD(port, baud)  # Auto-Connect to OBD
# REAL LIFE OBD USES BLUETOOTH CHANNEL 2!!!

# ========== OBD COMMANDS

# Get OBD response from specified command
def get_data(command, include_units: bool = False):
    response = connection.query(command)

    if not response.is_null():
        value = response.value

        if not include_units:
            value = value.magnitude

        return value

    return None


# RPMs
get_rpms = obd.commands.RPM  # Command
bound_cold_rpms = 2300
bound_rpms_redline = 4500  # REDLINING (Volvo s60)

# Speed
get_speed = obd.commands.SPEED
speed_last = -1  # Speed last second
speed_crazymode = 140  # Kerosene on 140 km/h
speed_record = 200 # Speed Record LETS GOOO
hard_brake_threshold = 14 # 20km

# Throttle position
get_throttle_pos = obd.commands.THROTTLE_POS
bound_throttle_flooring = 85 # percent

# Engine load - how hard the engine is working
get_engine_load = obd.commands.ENGINE_LOAD

# Coolant temperature - Celsius
get_cool_temp = obd.commands.COOLANT_TEMP
bound_cool_operating = 70

# Oil temperature - Celsius
get_oil_temp = obd.commands.OIL_TEMP

# Intake air Temperature - Celsius
get_intake_temp = obd.commands.INTAKE_TEMP

# Fuel level
get_fuel_level = obd.commands.FUEL_LEVEL
bounds_fuel_low = 15  # Percent

# ========== SOUND SETUP

# INIT
pygame.mixer.init()
pygame.mixer.set_num_channels(2)

# COOLDOWNS - seconds between playing
cooldowns = {
    "cold_engine_abuse": 600,
    "floor_gas": 300,
    "fuel_low": 1200,
    "hard_braking": 600,
    "redline": 30,
    "speed_record": 300,
    "startup": 604800
}

last_played = {}

# CHANNELS
ch_alert = pygame.mixer.Channel(0)
ch_ambient = pygame.mixer.Channel(1)

# LOAD SOUNDS
sound_dir = Path("audio")
sounds = {
    "ambient_speeding": [pygame.mixer.Sound(str(p)) for p in (sound_dir / "ambient_speeding").glob("*.wav")],
    "cold_engine_abuse": [pygame.mixer.Sound(str(p)) for p in (sound_dir / "cold_engine_abuse").glob("*.wav")],
    "floor_gas": [pygame.mixer.Sound(str(p)) for p in (sound_dir / "floor_gas").glob("*.wav")],
    "fuel_low": [pygame.mixer.Sound(str(p)) for p in (sound_dir / "fuel_low").glob("*.wav")],
    "hard_braking": [pygame.mixer.Sound(str(p)) for p in (sound_dir / "hard_braking").glob("*.wav")],
    "redline": [pygame.mixer.Sound(str(p)) for p in (sound_dir / "redline").glob("*.wav")],
    "speed_record": [pygame.mixer.Sound(str(p)) for p in (sound_dir / "speed_record").glob("*.wav")],
    "startup": [pygame.mixer.Sound(str(p)) for p in (sound_dir / "startup").glob("*.wav")],
}

# TRACK LAST PLAYED FOR AMBIENT
last_ambient = None

def can_play(label):
    now = time.time()
    last = last_played.get(label, 0)
    cooldown = cooldowns.get(label, 0)
    return (now - last) >= cooldown

def play_alert(label):
    if label in sounds:
        ch_alert.play(random.choice(sounds[label]))

def play_next_ambient():
    global last_ambient
    options = sounds.get("ambient", [])
    if not options:
        return
    next_sound = random.choice([s for s in options if s != last_ambient]) if len(options) > 1 else options[0]
    last_ambient = next_sound
    ch_ambient.play(next_sound)

def stop_ambient():
    ch_ambient.stop()

# ========== RUNTIME CODE
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
        #oil_temp = get_data(get_oil_temp)
        intake_temp = get_data(get_intake_temp)
        #fuel_level = get_data(get_fuel_level)
        fuel_level = 100

        # print(rpms, speed, throttle_pos, engine_load, coolant_temp, oil_temp, intake_temp, fuel_level, speed_last, sep="\n")

        # Startup greeting
        if can_play("startup"):
            play_alert("startup")
            last_played["startup"] = time.time()
            print("Connected to OBD")

        # Speed mode ambience
        if speed >= speed_crazymode and not ch_ambient.get_busy():
            play_next_ambient()
        else:
            stop_ambient()
            
        # You can trigger alerts here too
        if not ch_alert.get_busy():
            if speed_last - speed >= hard_brake_threshold and can_play("hard_braking"): # Hard braking
                play_alert("hard_braking")
                last_played["hard_braking"] = time.time()
                print("hard_braking")
            elif speed >= speed_record and can_play("speed_record"): # Speed record
                play_alert("speed_record")
                last_played["speed_record"] = time.time()
                print("speed_record")
            elif rpms >= bound_rpms_redline and can_play("redline"): # Redline
                play_alert("redline")
                last_played["redline"] = time.time()
                print("redline")
            elif rpms >= 2200 and coolant_temp < bound_cool_operating and can_play("cold_engine_abuse"): # Revving on cold engine
                play_alert("cold_engine_abuse")
                last_played["cold_engine_abuse"] = time.time()
                print("cold_engine_abuse")
            elif throttle_pos >= bound_throttle_flooring and can_play("floor_gas"):
                play_alert("floor_gas")
                last_played["floor_gas"] = time.time()
                print("floor_gas")
            elif not fuel_level == None and fuel_level <= bounds_fuel_low and can_play():
                play_alert("fuel_low")
                last_played["fuel_low"] = time.time()
                print("fuel_low")
            
        # Set speed to be last second speed at the end
        speed_last = float(speed)

    except Exception as e:
        print(f"Error: {e}")
        connection = obd.OBD(port, baud)

    # Cycle 1s
    time.sleep(1)
