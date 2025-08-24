# Design Document

## Overview

The Cashbook Dashboard will replace the current simple welcome screen with a comprehensive dashboard that allows users to manage multiple cashbooks. This design builds upon the existing CustomTkinter-based architecture while introducing a card-based layout similar to modern notebook management interfaces.

The dashboard will serve as the primary entry point for the application, providing users with immediate access to their financial data organized into separate cashbooks for different purposes (personal expenses, business, travel, etc.).

## Architecture

### Current Architecture Analysis
The existing application uses:
- CustomTkinter for modern GUI components with dark theme
- Single-window application structure with the `CashenseApp` class
- Simple button-based navigation
- Placeholder functionality for core features

### Proposed Architecture Changes
The dashboard will extend the current architecture by:
- Introducing a `CashbookManager` class for data management
- Implementing a card-based layout system using CustomTkinter frames
- Adding a data persistence layer for cashbook storage
- Maintaining the existing dark theme and styling consistency

### Component Hierarchy
```
CashenseApp (main window)
├── DashboardView (main dashboard container)
│   ├── HeaderSection (title and navigation)
│   ├── CashbookGrid (grid of cashbook cards)
│   │   ├── CreateCashbookCard (+ button card)
│   │   └── CashbookCard[] (individual cashbook cards)
│   └── FooterSection (status and additional actions)
└── CashbookManager (data management)
```

## Components and Interfaces

### 1. DashboardView Component
**Purpose:** Main container for the dashboard interface
**Responsibilities:**
- Layout management for the dashboard
- Coordination between header, grid, and footer sections
- Handling window resize events for responsive design

**Interface:**
```python
class DashboardView:
    def __init__(self, parent, cashbook_manager)
    def setup_layout()
    def refresh_cashbooks()
    def handle_resize(event)
```

### 2. CashbookGrid Component
**Purpose:** Grid layout container for cashbook cards
**Responsibilities:**
- Dynamic grid layout (2x2 for recent cashbooks)
- Card positioning and spacing
- Handling overflow with "See all" functionality

**Interface:**
```python
class CashbookGrid:
    def __init__(self, parent, cashbook_manager)
    def add_cashbook_card(cashbook_data)
    def remove_cashbook_card(cashbook_id)
    def update_layout()
    def show_all_cashbooks()
```

### 3. CashbookCard Component
**Purpose:** Individual cashbook representation
**Responsibilities:**
- Display cashbook information (name, date, entry count)
- Handle click events for opening cashbooks
- Provide context menu for management actions
- Visual feedback for hover states

**Interface:**
```python
class CashbookCard:
    def __init__(self, parent, cashbook_data, on_click_callback)
    def update_display()
    def show_context_menu(event)
    def handle_click()
    def handle_hover_enter()
    def handle_hover_leave()
```

### 4. CreateCashbookCard Component
**Purpose:** Special card for creating new cashbooks
**Responsibilities:**
- Display create new cashbook interface
- Handle new cashbook creation dialog
- Visual distinction from regular cashbook cards

**Interface:**
```python
class CreateCashbookCard:
    def __init__(self, parent, on_create_callback)
    def handle_click()
    def show_creation_dialog()
```

### 5. CashbookManager Component
**Purpose:** Data management and persistence
**Responsibilities:**
- CRUD operations for cashbooks
- Data persistence (JSON file storage initially)
- Cashbook metadata management
- Data validation

**Interface:**
```python
class CashbookManager:
    def create_cashbook(name, description="", category="")
    def get_recent_cashbooks(limit=4)
    def get_all_cashbooks()
    def update_cashbook(cashbook_id, **kwargs)
    def delete_cashbook(cashbook_id)
    def get_cashbook_stats(cashbook_id)
```

## Data Models

### Cashbook Model
```python
@dataclass
class Cashbook:
    id: str
    name: str
    description: str
    category: str
    created_date: datetime
    last_modified: datetime
    entry_count: int
    total_amount: float
    icon_color: str  # For visual differentiation
```

### CashbookMetadata Model
```python
@dataclass
class CashbookMetadata:
    total_cashbooks: int
    recent_activity: List[str]
    categories: List[str]
    last_backup: datetime
```

## Error Handling

### File System Errors
- **Scenario:** Cashbook data file corruption or inaccessibility
- **Handling:** Display error dialog with recovery options, create backup data file
- **User Experience:** Graceful degradation with option to recreate data

### Data Validation Errors
- **Scenario:** Invalid cashbook names or corrupted data entries
- **Handling:** Input validation with user-friendly error messages
- **User Experience:** Inline validation feedback, prevent invalid submissions

### Memory/Performance Errors
- **Scenario:** Large number of cashbooks causing performance issues
- **Handling:** Implement pagination and lazy loading for cashbook grid
- **User Experience:** Smooth scrolling and responsive interface

### Network/Sync Errors (Future)
- **Scenario:** Cloud sync failures (for future cloud integration)
- **Handling:** Offline mode with sync retry mechanisms
- **User Experience:** Clear sync status indicators

## Testing Strategy

### Unit Testing
- **CashbookManager:** Test all CRUD operations, data validation, file I/O
- **Individual Components:** Test component initialization, event handling, state management
- **Data Models:** Test data serialization/deserialization, validation rules

### Integration Testing
- **Dashboard Flow:** Test complete user workflows from dashboard to cashbook creation
- **Data Persistence:** Test data saving/loading across application restarts
- **UI Interactions:** Test card interactions, context menus, responsive layout

### UI Testing
- **Visual Regression:** Ensure consistent styling across different screen sizes
- **Accessibility:** Test keyboard navigation, screen reader compatibility
- **Performance:** Test with varying numbers of cashbooks (1, 10, 100+)

### User Acceptance Testing
- **Workflow Testing:** Complete user scenarios from dashboard navigation to cashbook management
- **Usability Testing:** Interface intuitiveness, error recovery, visual feedback
- **Cross-Platform Testing:** Ensure consistent behavior across Windows, macOS, Linux

## Implementation Notes

### Styling Consistency
- Maintain existing dark theme using CustomTkinter's built-in theming
- Use consistent spacing (10px, 20px, 30px) following current patterns
- Implement hover effects using CustomTkinter's state management
- Color scheme: Use existing blue theme with accent colors for different cashbook categories

### Performance Considerations
- Implement lazy loading for cashbook cards to handle large numbers of cashbooks
- Use efficient grid layout algorithms for responsive design
- Cache cashbook metadata to reduce file I/O operations
- Implement debounced search/filter functionality for future enhancements

### Data Storage
- Initial implementation: JSON file storage in user's application data directory
- File structure: `~/.cashense/cashbooks.json` for metadata, individual files for cashbook data
- Backup strategy: Automatic daily backups with rotation (keep last 7 days)
- Migration path: Design data models to support future database integration

### Responsive Design
- Grid layout adapts from 2x2 (desktop) to 1x4 (narrow windows)
- Minimum window size: 600x400 (matching current constraints)
- Card sizing: Fixed aspect ratio with flexible dimensions
- Text scaling: Responsive font sizes based on card dimensions