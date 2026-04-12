import platform
import subprocess

system = platform.system()

if system == "Windows":
    from pycaw.pycaw import AudioUtilities

    def _get_volume():
        """Get the endpoint volume interface (new pycaw API)."""
        speakers = AudioUtilities.GetSpeakers()
        return speakers.EndpointVolume

    def set_volume(percent: int) -> int:
        """Set system volume instantly (0-100)."""
        percent = max(0, min(100, percent))
        vol = _get_volume()
        vol.SetMasterVolumeLevelScalar(percent / 100, None)
        return percent

    def get_volume() -> int:
        vol = _get_volume()
        return int(vol.GetMasterVolumeLevelScalar() * 100)

    def mute():
        vol = _get_volume()
        vol.SetMute(1, None)

    def unmute():
        vol = _get_volume()
        vol.SetMute(0, None)

    def is_muted() -> bool:
        vol = _get_volume()
        return bool(vol.GetMute())


elif system == "Darwin":
    def set_volume(percent: int) -> int:
        percent = max(0, min(100, percent))
        subprocess.run(
            ["osascript", "-e", f"set volume output volume {percent}"],
            capture_output=True,
        )
        return percent

    def get_volume() -> int:
        result = subprocess.run(
            ["osascript", "-e", "output volume of (get volume settings)"],
            capture_output=True,
            text=True,
        )
        return int(result.stdout.strip())

    def mute():
        subprocess.run(
            ["osascript", "-e", "set volume output muted true"],
            capture_output=True,
        )

    def unmute():
        subprocess.run(
            ["osascript", "-e", "set volume output muted false"],
            capture_output=True,
        )

    def is_muted() -> bool:
        result = subprocess.run(
            ["osascript", "-e", "output muted of (get volume settings)"],
            capture_output=True,
            text=True,
        )
        return result.stdout.strip() == "true"


else:
    def set_volume(percent: int) -> int:
        percent = max(0, min(100, percent))
        subprocess.run(
            ["amixer", "-q", "sset", "Master", f"{percent}%"],
            capture_output=True,
        )
        return percent

    def get_volume() -> int:
        result = subprocess.run(
            ["amixer", "sget", "Master"], capture_output=True, text=True
        )
        for line in result.stdout.split("\n"):
            if "%" in line:
                start = line.index("[") + 1
                end = line.index("%")
                return int(line[start:end])
        return 0

    def mute():
        subprocess.run(
            ["amixer", "-q", "sset", "Master", "mute"],
            capture_output=True,
        )

    def unmute():
        subprocess.run(
            ["amixer", "-q", "sset", "Master", "unmute"],
            capture_output=True,
        )

    def is_muted() -> bool:
        result = subprocess.run(
            ["amixer", "sget", "Master"], capture_output=True, text=True
        )
        return "[off]" in result.stdout


def set_brightness(percent: int) -> int:
    percent = max(0, min(100, percent))
    if system == "Windows":
        try:
            import wmi
            c = wmi.WMI(namespace="wmi")
            methods = c.WmiMonitorBrightnessMethods()[0]
            methods.WmiSetBrightness(percent, 0)
        except Exception:
            pass
    return percent