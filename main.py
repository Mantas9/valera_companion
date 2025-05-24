import obd
import time
import pygame
import random
from pathlib import Path

debug = False

# ========== OBD CONNECTION BASICS
port = "/dev/rfcomm0"
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
bound_rpms_redline = 1500  # REDLINING (Volvo s60)

# Speed
get_speed = obd.commands.SPEED
speed_last = -1  # Speed last second
speed_crazymode = 140  # Kerosene on 140 km/h
speed_record = 170 # Speed Record LETS GOOO
hard_brake_threshold = 16 # 20km

# Throttle position
get_throttle_pos = obd.commands.THROTTLE_POS
bound_throttle_flooring = 95 # percent

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
pygame.mixer.pre_init(frequency=22050, size=-16, channels=1, buffer=8192)
pygame.mixer.init()
pygame.mixer.set_num_channels(8)

silent_sound = pygame.mixer.Sound(buffer=b'\x00' * 100)
silent_sound.play()
pygame.time.wait(100)

# CHANNELS
ch_alert = pygame.mixer.Channel(0)
ch_ambient = pygame.mixer.Channel(1)

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

# LOAD SOUNDS
sound_dir = Path("/home/admin/valera_companion/audio")
sounds = {
    "ambient": [pygame.mixer.Sound(str(p)) for p in (sound_dir / "ambient").glob("*.wav")],
    "cold_engine_abuse": [pygame.mixer.Sound(str(p)) for p in (sound_dir / "cold_engine_abuse").glob("*.wav")],
    "floor_gas": [pygame.mixer.Sound(str(p)) for p in (sound_dir / "floor_gas").glob("*.wav")],
    "fuel_low": [pygame.mixer.Sound(str(p)) for p in (sound_dir / "fuel_low").glob("*.wav")],
    "hard_braking": [pygame.mixer.Sound(str(p)) for p in (sound_dir / "hard_braking").glob("*.wav")],
    "redline": [pygame.mixer.Sound(str(p)) for p in (sound_dir / "redline").glob("*.wav")],
    "speed_record": [pygame.mixer.Sound(str(p)) for p in (sound_dir / "speed_record").glob("*.wav")],
    "startup": [pygame.mixer.Sound(str(p)) for p in (sound_dir / "startup").glob("*.wav")],
}

time.sleep(0.5)

# TRACK LAST PLAYED FOR AMBIENT
last_ambient = None

def can_play(label):
    now = time.time()
    last = last_played.get(label, 0)
    cooldown = cooldowns.get(label, 0)
    return (now - last) >= cooldown

def play_alert(label):
    if label in sounds and can_play(label) and not ch_alert.get_busy():
        ch_alert.play(random.choice(sounds[label]))
        last_played[label] = time.time()
        print(label)

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

time.sleep(1)

# ========== RUNTIME CODE
while True:
    
    speed = 0
    try:
        # Check for connection
        if not connection.is_connected():
            print("Reconnecting to OBD...")
            connection = obd.OBD(port, baud)
        
        # Get responses
        rpms = get_data(get_rpms, debug)
        speed = get_data(get_speed, debug)
        engine_load = get_data(get_engine_load, debug)
        coolant_temp = get_data(get_cool_temp, debug)
        intake_temp = get_data(get_intake_temp, debug)
        

        if debug:
            print("RPMS: " + str(rpms),"SPEED: " + str(speed), "THROTTLE POS:", "ENGINE LOAD: " + str(engine_load), "COOLANT TEMP: " + str(coolant_temp), "INTAKE TEMP: " + str(intake_temp), "LAST SPEED: " + str(speed_last), sep="\n")
            print("\n")
            if not speed == None:
                speed_last = speed.magnitude
        else:
            # Startup greeting
            if can_play("startup"):
                play_alert("startup")
                last_played["startup"] = time.time()
                print("Connected to OBD")

            # Speed mode ambience
            if not speed == None and speed >= speed_crazymode and not ch_ambient.get_busy():
                play_next_ambient()
            elif not speed == None and speed < speed_crazymode:
                stop_ambient()
                
            if not speed == None and not speed_last == None and speed_last - speed >= hard_brake_threshold and can_play("hard_braking"): # Hard braking
                play_alert("hard_braking")
            elif not speed == None and speed >= speed_record and can_play("speed_record"): # Speed record
                play_alert("speed_record")
            elif not rpms == None and rpms >= bound_rpms_redline and can_play("redline"): # Redline
                play_alert("redline")
                
            # You can trigger alerts here too
            if not ch_alert.get_busy():
                if not rpms == None and rpms >= 2200 and coolant_temp < bound_cool_operating and can_play("cold_engine_abuse"): # Revving on cold engine
                    play_alert("cold_engine_abuse")
              
                
            # Set speed to be last second speed at the end
            if not speed == None:
                speed_last = speed
    except Exception as e:
        print(f"Error: {e}")
        connection = obd.OBD(port, baud)

    
    # Cycle 1s
    time.sleep(1)
