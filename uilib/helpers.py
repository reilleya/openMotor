from PyQt6.QtCore import Qt

FLAGS_NO_ICON = Qt.WindowType.Dialog | Qt.WindowType.CustomizeWindowHint | Qt.WindowType.WindowTitleHint | Qt.WindowType.WindowCloseButtonHint

def excludeKeys(d, keys):
	return {k:v for k,v in d.items() if k not in keys}
