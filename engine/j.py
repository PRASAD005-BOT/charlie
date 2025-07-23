import os
import glob

# Define the directories to search for the DLL file
search_paths = [
  
    r'C:\Program Files\Python312',  # Typical path for Python 3.12 installation
    r'C:\Program Files (x86)\Python312',  # 32-bit Python installation
    r'C:\Users\YourUsername\AppData\Local\Programs\Python\Python312',  # User-specific Python installation
]

# Iterate through the search paths
dll_path = None
for path in search_paths:
    search_pattern = os.path.join(path, '**', 'python312.dll')
    dll_files = glob.glob(search_pattern, recursive=True)
    if dll_files:
        dll_path = dll_files[0]
        break

if dll_path:
    print(f'Found python312.dll at: {dll_path}')
else:
    print('python312.dll not found on your system.')
