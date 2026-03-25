# Raspberry Pi GPIO buzzer — only works on Pi hardware
# On a regular PC this module is safely ignored

def buzz_alert(pin=18, duration=1.0):
    try:
        import RPi.GPIO as GPIO
        import time
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(pin, GPIO.OUT)
        GPIO.output(pin, GPIO.HIGH)
        time.sleep(duration)
        GPIO.output(pin, GPIO.LOW)
        GPIO.cleanup()
    except ImportError:
        pass  # Not on a Raspberry Pi — skip silently
    except Exception as e:
        print(f"[BUZZER] Error: {e}")