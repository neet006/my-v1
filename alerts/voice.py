import threading

_tts_lock = threading.Lock()


def speak_alert_async(message="Warning. Driver is sleeping. Please wake up immediately."):
    def _speak():
        if _tts_lock.acquire(blocking=False):
            try:
                import pyttsx3
                engine = pyttsx3.init()
                engine.setProperty('rate', 145)
                engine.setProperty('volume', 1.0)
                engine.say(message)
                engine.runAndWait()
                engine.stop()
            except Exception as e:
                print(f"[VOICE] TTS error: {e}")
            finally:
                _tts_lock.release()

    threading.Thread(target=_speak, daemon=True).start()
