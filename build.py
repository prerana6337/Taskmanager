import os
import sys
import shutil
import subprocess

def clean_build():
    """Clean build directories"""
    dirs_to_clean = ['build', 'dist']
    for dir_name in dirs_to_clean:
        if os.path.exists(dir_name):
            shutil.rmtree(dir_name)
    
    # Clean spec files
    for file in os.listdir('.'):
        if file.endswith('.spec'):
            os.remove(file)

def install_requirements():
    """Install required packages"""
    subprocess.check_call([sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'])

def build_executable():
    """Build the executable using PyInstaller"""
    # PyInstaller command with options
    pyinstaller_path = os.path.join(os.path.dirname(sys.executable), 'Scripts', 'pyinstaller.exe')
    if not os.path.exists(pyinstaller_path):
        pyinstaller_path = os.path.join(os.path.expanduser('~'), 'AppData', 'Roaming', 'Python', 'Python311', 'Scripts', 'pyinstaller.exe')
    
    if not os.path.exists(pyinstaller_path):
        raise FileNotFoundError("Could not find pyinstaller.exe. Please ensure it's installed correctly.")
    
    # PyInstaller command with options
    command = [
        pyinstaller_path,
        '--name=TaskManager',
        '--windowed',
        '--onefile',
        '--clean',
        '--add-data=tasks.db;.',  # Include database file
        'task_manager.py'
    ]
    
    subprocess.check_call(command)

def create_distribution():
    """Create distribution package"""
    # Create dist directory if it doesn't exist
    if not os.path.exists('dist'):
        os.makedirs('dist')
    
    # Copy necessary files to dist
    files_to_copy = [
        'README.md',
        'requirements.txt'
    ]
    
    for file in files_to_copy:
        if os.path.exists(file):
            shutil.copy2(file, 'dist')

def main():
    print("Starting build process...")
    
    print("Cleaning previous build...")
    clean_build()
    
    print("Installing requirements...")
    install_requirements()
    
    print("Building executable...")
    build_executable()
    
    print("Creating distribution package...")
    create_distribution()
    
    print("Build completed successfully!")
    print("The executable can be found in the 'dist' directory.")

if __name__ == '__main__':
    main()
