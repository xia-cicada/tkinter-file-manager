from blinker import signal

signal_status_change = signal("status change")
signal_path_change = signal("path change")