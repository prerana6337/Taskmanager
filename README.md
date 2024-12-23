# Task Manager Application

A modern desktop task management application built with Python and Tkinter.

## Features

- Add, update, and delete tasks
- Set task priorities and due dates
- Mark tasks as complete
- Search and filter tasks
- Recycle bin for deleted tasks
- Modern and user-friendly interface

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd task-manager
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Running the Application

### Development Mode
Run the application directly with Python:
```bash
python task_manager.py
```

### Executable Version
The application can be run as a standalone executable:

1. Windows: Run `TaskManager.exe` from the `dist` folder
2. The executable includes all dependencies and doesn't require Python installation

## Building the Executable

To create the executable:

1. Install PyInstaller:
```bash
pip install pyinstaller
```

2. Build the executable:
```bash
pyinstaller --name TaskManager --windowed --onefile --icon=app_icon.ico task_manager.py
```

The executable will be created in the `dist` folder.

## Usage

1. **Adding Tasks**
   - Fill in task details (title, description, due date, priority)
   - Click "Add Task"

2. **Managing Tasks**
   - Select a task to update or delete
   - Use action buttons for task management
   - Search tasks using the search bar

3. **Recycle Bin**
   - Access deleted tasks from the Recycle Bin
   - Restore or permanently delete tasks

## Data Storage

Tasks are stored in a local SQLite database (`tasks.db`)
