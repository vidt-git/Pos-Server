# Timeboxing Feature

## Overview
Added timeboxing functionality to the Task Manager application. Tasks can now have optional time ranges and be visualized in a calendar-style timebox view similar to Microsoft Teams calendar.

## Features Added

### 1. Optional Time Fields
- `time_from`: Start time in HH:MM format (optional)
- `time_to`: End time in HH:MM format (optional)
- Tasks without time fields continue to work as before

### 2. Dual View System
- **List View**: Original task list view
- **Timebox View**: Calendar-style visualization with time slots

### 3. Timebox View Features
- ✅ 15-minute time intervals (from 00:00 to 23:45)
- ✅ Square boxes of equal size (80px height per 15-min slot)
- ✅ Task boxes span multiple slots based on duration
- ✅ Live current time clock display
- ✅ Support for overlapping tasks (displayed side-by-side)
- ✅ Visual distinction for completed tasks (grayed out)
- ✅ Checkbox to toggle completion
- ✅ Delete button on each task box
- ✅ Responsive hover effects

### 4. UI Enhancements
- Time picker inputs in the task creation form
- Toggle buttons to switch between List and Timebox views
- Real-time clock showing current time in Timebox view

## Usage

### Creating a Task with Time
1. Fill in task name and amount
2. Optionally select start time (From) and end time (To)
3. Click "Add Task"
4. Task appears in both List and Timebox views

### Viewing Tasks
- **List View**: Traditional list showing all tasks
- **Timebox View**: Calendar grid showing tasks in their time slots

### Task Operations in Timebox View
- Click checkbox to mark complete/incomplete
- Click trash icon to delete task
- Hover over task for visual feedback

## Technical Details

### Data Model Changes
- Added `time_from` and `time_to` to `TaskCreate`, `Task`, and `DoneTask` models
- Fields are optional (defaults to None)

### API Changes
- `POST /api/tasks` now accepts optional `time_from` and `time_to` fields
- `GET /api/tasks` returns tasks with time information

### Frontend
- JavaScript generates 96 time slots (24 hours × 4 slots/hour)
- Tasks are positioned and sized dynamically based on duration
- Overlapping detection displays tasks side-by-side
- Real-time clock updates every second

## Styling
- Purple gradient theme matching existing design
- Square boxes with consistent 80px height per 15-minute interval
- Responsive design for mobile devices
- Smooth transitions and hover effects

## Future Enhancements
- Drag-and-drop to reschedule tasks
- Click on empty slots to create tasks
- Week/month view options
- Task color coding by category
- Conflict detection for overlapping tasks
