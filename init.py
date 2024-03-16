import platform

if platform.system() == 'Windows':
	import os, PySide6, shiboken6
	with os.add_dll_directory(os.path.dirname(PySide6.__file__)), \
	     os.add_dll_directory(os.path.dirname(shiboken6.__file__)):
		from .LimeReport import *
else:
	# Runtime library dependencies resolved via rpath
	from .LimeReport import *