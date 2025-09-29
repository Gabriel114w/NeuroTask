# NeuroTask - ADHD Task Organizer

## Overview

NeuroTask is a task organization application specifically designed for people with ADHD. The application provides a user-friendly interface for managing tasks with features tailored to ADHD needs, including visual cues, notifications, and simplified task management. Built with Streamlit for the web interface, the application emphasizes accessibility and ease of use through ADHD-friendly design patterns.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### Frontend Architecture
- **Framework**: Streamlit web application framework
- **Design Philosophy**: ADHD-friendly interface with custom CSS styling
- **State Management**: Streamlit session state for maintaining user sessions and application state
- **UI Components**: Custom styled buttons, task items with visual indicators for completion status
- **Responsive Design**: Centered layout optimized for focus and reduced distractions

### Backend Architecture
- **Data Storage**: JSON file-based persistence for user data and session management
- **File Structure**: 
  - `users.json` for user account information
  - `session.json` for session persistence
- **Utility Functions**: Centralized utility module for data operations and validation
- **Notification System**: Console-based task notifications with threading support for background processing

### Authentication & Session Management
- **User Authentication**: Simple email/username and password system
- **Session Persistence**: File-based session storage to maintain user state across browser sessions
- **User Data**: JSON-based user profiles with task management capabilities

### Task Management System
- **Task Structure**: Tasks with titles, descriptions, completion status, and timing information
- **Visual Indicators**: Color-coded task items (completed vs pending) for quick visual recognition
- **Time Management**: Task scheduling with time formatting for better readability
- **Edit Functionality**: In-place task editing capabilities

### Notification Architecture
- **Background Processing**: Threading implementation for non-blocking notification delivery
- **Notification Types**: Task reminders with customizable messages
- **Timing System**: Date-based checking system to prevent duplicate notifications

## External Dependencies

### Core Framework Dependencies
- **Streamlit**: Primary web application framework for the user interface
- **Threading**: Python standard library for background notification processing
- **JSON**: Built-in Python module for data serialization and storage
- **DateTime**: Python standard library for time and date management
- **OS**: File system operations and path management
- **Re**: Regular expressions for email validation

### Utility Dependencies
- Custom utility functions for data persistence, validation, and formatting
- No external database systems - relies on local file storage for simplicity and offline capability

### Potential Future Integrations
- Email notification services for task reminders
- Calendar integration for deadline management
- Cloud storage for data synchronization across devices