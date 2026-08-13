# Warehouse Vision

DETAILED WMS FRONTEND PROMPT FOR LOVABLE

Build a professional Warehouse Management System (WMS) frontend with enterprise-grade UI/UX 
matching modern inventory management tools (similar design language to Figma Inventory case study).

===========================================
PART 1: DESIGN SYSTEM & VISUAL HIERARCHY
===========================================

### COLOR PALETTE

**Primary Colors:**
- Primary Green: #10B981 (action buttons, active states, success indicators)
- Primary Dark Blue: #1F2937 (backgrounds, text, navigation)
- Charcoal: #374151 (secondary text, borders)

**Background Colors:**
- Dark Background: #111827 (main app background)
- Card Background: #1F2937 (cards, modals, tables)
- Hover Background: #2D3748 (hover states)
- Input Background: #0F172A (input fields)

**Status Colors:**
- Success Green: #10B981
- Warning Yellow: #F59E0B
- Danger Red: #EF4444
- Info Blue: #3B82F6
- Neutral Gray: #9CA3AF

**Text Colors:**
- Primary Text: #F3F4F6 (headings, primary content)
- Secondary Text: #D1D5DB (descriptions, secondary info)
- Muted Text: #9CA3AF (hints, disabled states)

**Border & Dividers:**
- Border Color: #374151
- Hover Border: #4B5563

### TYPOGRAPHY

**Font Family:**
- Primary: Inter or SF Pro Display (system fonts)
- Monospace: Fira Code (for codes, IDs, barcodes)

**Font Sizes & Weights:**
- H1: 32px, weight 700, line-height 1.2
- H2: 24px, weight 700, line-height 1.35
- H3: 20px, weight 600, line-height 1.4
- Body Large: 16px, weight 500, line-height 1.5
- Body Regular: 14px, weight 400, line-height 1.5
- Body Small: 12px, weight 400, line-height 1.5
- Caption: 11px, weight 500, line-height 1.4
- Label: 12px, weight 600, line-height 1.4

**Letter Spacing:**
- Headers: -0.5px
- Body: 0px
- Labels: 0.5px

### SPACING SYSTEM (8px grid)

- xs: 4px
- sm: 8px
- md: 16px
- lg: 24px
- xl: 32px
- 2xl: 48px
- 3xl: 64px

Use consistent spacing for padding/margins throughout.

### BORDER RADIUS

- Buttons/Inputs: 8px
- Cards/Modals: 12px
- Pills/Badges: 20px
- Icons: 6px

### SHADOWS & DEPTH

- Elevation 1 (cards): 0 1px 3px rgba(0,0,0,0.12), 0 1px 2px rgba(0,0,0,0.24)
- Elevation 2 (modals): 0 3px 6px rgba(0,0,0,0.16), 0 3px 6px rgba(0,0,0,0.23)
- Elevation 3 (dropdowns): 0 10px 20px rgba(0,0,0,0.19), 0 6px 6px rgba(0,0,0,0.23)

===========================================
PART 2: LAYOUT & STRUCTURE
===========================================

### MAIN LAYOUT STRUCTURE



┌─────────────────────────────────────────────┐
│  HEADER (64px height)                        │
│  Logo | Search | Notifications | User Menu  │
├──────────┬──────────────────────────────────┤
│          │                                   │
│  SIDEBAR │  MAIN CONTENT AREA                │
│ (256px)  │                                   │
│          │  - Breadcrumbs                    │
│          │  - Page Title + Actions           │
│          │  - Content (Tables/Cards/Forms)   │
│          │                                   │
└──────────┴──────────────────────────────────┘


**Header (64px):**
- Logo (left): 32x32px icon + "Whitfield WMS" text
- Search bar (center): w-320px, placeholder "Search orders, tickets..."
- Right icons: Notifications (bell), User menu (avatar dropdown)
- Spacing: 16px padding horizontal/vertical

**Sidebar (256px fixed):**
- Scrollable
- Logo + text at top (48px)
- Menu items list
- Settings/Help at bottom (sticky)
- Collapse button (tablet/mobile)
- Active indicator: left border (4px green)
- Hover state: background highlight
- Smooth transitions (200ms)

**Main Content:**
- Min 64px top padding (below header)
- 24px left/right padding
- Max-width: 1440px (centered)

### RESPONSIVE BREAKPOINTS

- Mobile: < 640px (sidebar hidden, hamburger menu)
- Tablet: 640px - 1024px (sidebar collapsed to icons)
- Desktop: > 1024px (full layout)

===========================================
PART 3: COMPONENT SPECIFICATIONS
===========================================

### BUTTONS

**Primary Button:**
- Background: #10B981
- Text: white, 14px, weight 600
- Padding: 10px 16px
- Border-radius: 8px
- Icon + text spacing: 8px
- Hover: brightness 110%
- Active: brightness 90%
- Disabled: opacity 50%
- Transition: 150ms

**Secondary Button:**
- Background: #2D3748
- Text: #F3F4F6
- Border: 1px #374151
- Same padding/radius as primary
- Hover: background #374151
- Disabled: opacity 50%

**Ghost Button:**
- Background: transparent
- Text: #10B981
- Border: 1px #10B981
- Hover: background rgba(16, 185, 129, 0.1)
- Active: background rgba(16, 185, 129, 0.2)

**Icon Button:**
- 40px x 40px
- Icon centered
- Background: transparent
- Hover: background #2D3748
- Rounded: 8px

**Danger Button (Delete/Revoke):**
- Background: #EF4444
- Text: white
- Same styling as primary
- Hover: brightness 110%
- Requires confirmation modal

### FORM INPUTS

**Text Input:**
- Background: #0F172A
- Border: 1px #374151
- Text: #F3F4F6, 14px
- Placeholder: #9CA3AF
- Padding: 10px 12px
- Border-radius: 8px
- Focus: border #10B981 (2px), box-shadow: 0 0 0 3px rgba(16,185,129,0.1)
- Error state: border #EF4444
- Disabled: opacity 50%, background #1F2937
- Transition: 150ms

**Select Dropdown:**
- Same styling as text input
- Arrow icon (right-aligned)
- Dropdown options: dark background, highlight on hover
- Option padding: 10px 12px
- Option hover: background #2D3748
- Max-height: 300px (scrollable)

**Checkbox:**
- Size: 18x18px
- Border: 2px #374151
- Checked: background #10B981, border #10B981
- Border-radius: 4px
- Checkmark: white, 2px stroke
- Label: 14px, left-margin 8px
- Hover: border #10B981

**Radio Button:**
- Size: 18x18px
- Border: 2px #374151
- Checked: border 6px #10B981, inner circle
- Border-radius: 50%
- Label: 14px, left-margin 8px

**File Upload:**
- Drag-and-drop zone: dashed border, 2px #374151
- Hover: border #10B981, background rgba(16,185,129,0.05)
- Icon: 40x40px, #9CA3AF
- Text: "Drag files here or click to browse"
- Accepted: PNG, JPG, PDF
- Max size: 5MB

**Search Input:**
- Width: 100% or fixed 320px
- Icon: magnifying glass (left, 16px)
- Placeholder: "Search..."
- Padding: 10px 12px 10px 36px
- Clear button (X): appears on focus with text
- Debounce: 300ms before search

### TABLES

**Table Structure:**
- Header row background: #1F2937
- Header text: #D1D5DB, 12px, weight 600
- Header border-bottom: 1px #374151
- Row height: 52px
- Row padding: 12px 16px
- Border-bottom: 1px #374151

**Row Styling:**
- Hover background: #2D3748 (smooth 150ms)
- Selected: background #2D3748, left border 4px #10B981
- Zebra striping: optional (alternate #1F2937 and #111827)

**Column Types:**
- Checkbox column: 40px width
- Action column (edit/delete): 60px width
- ID/SKU: monospace, 12px, color #9CA3AF
- Status badge: pill shape, colored background
- Timestamp: 12px, #9CA3AF
- Numbers: right-aligned

**Pagination:**
- Below table: "Showing 1-50 of 250 results"
- Controls: Previous button, page numbers (max 7), Next button
- Active page: background #10B981, white text
- Disabled state: opacity 50%
- Jump to page: input field (50px width)

**Sortable Columns:**
- Hover: cursor pointer, background slightly lighter
- Sorted column: background #2D3748
- Sort icon: chevron up/down, 14px, #10B981
- Indicate ascending/descending clearly

### CARDS & PANELS

**Data Card:**
- Background: #1F2937
- Border: 1px #374151
- Padding: 20px
- Border-radius: 12px
- Shadow: elevation 1
- Title: H3, #F3F4F6
- Value: H2, #10B981
- Subtitle: 12px, #9CA3AF
- Hover: border #10B981, shadow elevation 2

**Status Badge:**
- Padding: 4px 12px
- Border-radius: 20px (pill)
- Font: 12px, weight 600
- Colors:
  - PENDING: background #374151, text #F3F4F6
  - ACTIVE: background rgba(16,185,129,0.2), text #10B981
  - INSPECTED: background rgba(59,130,246,0.2), text #3B82F6
  - STORED: background rgba(16,185,129,0.2), text #10B981
  - PACKED: background rgba(245,158,11,0.2), text #F59E0B
  - SHIPPED: background rgba(16,185,129,0.2), text #10B981
  - ERROR: background rgba(239,68,68,0.2), text #EF4444

**Alert/Notification:**
- Padding: 12px 16px
- Border-left: 4px colored
- Border-radius: 8px
- Icon: left-aligned, 20x20px
- Title: 14px, weight 600
- Message: 13px
- Close button: icon, right-aligned
- Auto-dismiss: 5 seconds (with progress bar)

### MODALS & DIALOGS

**Modal Structure:**
- Overlay: background rgba(0,0,0,0.7)
- Modal background: #1F2937
- Border: 1px #374151
- Border-radius: 12px
- Min-width: 400px, Max-width: 600px
- Box-shadow: elevation 3
- Animation: fade + scale (200ms, easing cubic-bezier(0.4, 0, 0.2, 1))

**Modal Header:**
- Title: H2, #F3F4F6
- Close button: X icon, top-right
- Border-bottom: 1px #374151
- Padding: 20px

**Modal Body:**
- Padding: 20px
- Max-height: 60vh (scrollable)

**Modal Footer:**
- Padding: 16px 20px
- Border-top: 1px #374151
- Buttons: right-aligned
- Button spacing: 12px
- Primary action: right
- Cancel button: left

**Form Modal Spacing:**
- Form group spacing: 16px vertical
- Label: 12px, weight 600, #D1D5DB
- Input below label: 4px spacing
- Helper text: 11px, #9CA3AF
- Error message: 11px, #EF4444
- Checkboxes/radios: 8px spacing

### NAVIGATION & BREADCRUMBS

**Breadcrumbs:**
- Font: 12px
- Color: #9CA3AF
- Separator: / (8px padding)
- Last item: #F3F4F6, no link
- Hover: color #10B981
- Clickable except last
- Padding: 8px top/bottom

**Sidebar Menu Item:**
- Icon: 18x18px, left-aligned
- Label: 14px
- Padding: 8px 12px left, 8px 16px right
- Height: 36px
- Spacing between items: 2px
- Active: background #2D3748, left border 4px #10B981, text #10B981
- Hover: background #2D3748
- Disabled: opacity 50%
- Transition: 150ms

**Submenu:**
- Indent: 20px left
- Font-size: 13px
- Same hover/active as parent
- Chevron rotation on expand: 90deg (200ms)

### LOADING & EMPTY STATES

**Loading Spinner:**
- Size: 40x40px (default), 24x24px (small)
- Color: #10B981
- Animation: rotate 360deg (1s, linear, infinite)
- Overlay: rgba(0,0,0,0.3) for page-level loading

**Skeleton Loader:**
- Background: #2D3748
- Shimmer: linear gradient animation (left to right, 2s infinite)
- Gradient: #2D3748 → #374151 → #2D3748
- Shapes: rect for cards/rows, circle for avatars
- Height: 16px (text), 40px (rows), 40x40px (avatars)

**Empty State:**
- Icon: 64x64px, #9CA3AF
- Title: H3, #F3F4F6
- Description: 14px, #9CA3AF
- CTA Button: primary button below
- Spacing: 24px vertical between elements
- Centered in container

**Error State:**
- Alert background: rgba(239,68,68,0.1)
- Border: 1px #EF4444
- Icon: error circle, 24x24px, #EF4444
- Title: H3, #EF4444
- Message: 14px, #D1D5DB
- Retry button: secondary
- Error code: monospace, 11px, #9CA3AF

### DROPDOWNS & MENUS

**Dropdown Menu:**
- Min-width: 200px
- Background: #1F2937
- Border: 1px #374151
- Border-radius: 8px
- Shadow: elevation 3
- Padding: 4px 0
- Animation: fade + slide-up (150ms)

**Menu Item:**
- Height: 36px
- Padding: 8px 12px
- Font: 14px, #F3F4F6
- Hover: background #2D3748
- Active: background #2D3748, left border 4px #10B981
- Icon: left-aligned, 16x16px
- Icon + text spacing: 12px
- Disabled: opacity 50%
- Divider: 1px #374151, margin 4px 0

**User Menu Dropdown:**
- Avatar: 32x32px, 50% border-radius
- User info: name (14px), email (12px, #9CA3AF)
- Menu items: Settings, Activity, Help, Logout
- Logout: red text (#EF4444)

===========================================
PART 4: PAGE-SPECIFIC DESIGNS
===========================================

### DASHBOARD (OWNER/MANAGER/STAFF)

**Layout:**
- Breadcrumb: Dashboard
- Page title: H1, with quick action buttons (right-aligned)
- Grid of metric cards: 4 columns on desktop, 2 on tablet, 1 on mobile
- Charts section: 2 columns
- Recent activity/feed: full width below

**Metric Cards:**
- 4 cards in row: Total Orders, Total Revenue, Avg Fulfillment Time, Pending Approvals
- Card layout: icon (top-left, 40x40px) | title (top) + value (large, green) + trend (↑ 12%)
- Value color: #10B981, font 28px, weight 700
- Trend: 12px, green (↑) or red (↓)
- Sparkline chart (small, 80x20px) in bottom-right corner

**Role-Specific Cards:**
- OWNER: System health, total staff, warehouse count, revenue
- MANAGER: Warehouse metrics, approval queue count, today's arrivals
- STAFF: Tasks assigned, items scanned, orders packed

**Charts:**
- 2-column grid
- Left: Order Status Donut Chart (pie chart showing PENDING/RESERVED/PACKED/SHIPPED)
- Right: Warehouse Comparison Bar Chart (warehouses vs order count)
- Charts: Chart.js or Recharts, green accent color
- Legend below each chart

**Recent Activity Table:**
- Full width
- Columns: Timestamp, Event Type, Actor, Order/Ticket ID, Status
- Limit: 10 rows
- View All link at bottom

### ORDERS & FULFILLMENT PAGE

**Header Section:**
- Breadcrumb: Dashboard > Orders
- Title: "Orders" (H1)
- Right-aligned buttons: "Filter" (icon), "Export" (icon), "Create Order" (primary)

**Filter Bar (sticky below header):**
- Status filter: Multi-select dropdown (PENDING, RESERVED, PACKED, SHIPPED)
- Date range: From/To date pickers (calendar icon)
- Search: Search by order ID / customer name
- Warehouse filter: Dropdown
- Clear all: link
- Spacing: horizontal, with dividers

**Main Table:**
- Columns: 
  - Checkbox (select row)
  - Order ID (monospace, clickable → detail view)
  - Customer Name (14px)
  - Warehouse (12px, #9CA3AF)
  - Items (count, 12px)
  - Status (badge: color-coded)
  - Created Date (12px, #9CA3AF)
  - Actions (3-dot menu: View, Edit, Delete)
- Row hover: background highlight, "View" button appears
- Multi-select: "Delete Selected" button appears at top

**Order Detail Modal/Page:**
- Header: "Order #ORD-1001" + status badge (top)
- 2-column layout:
  - Left (60%):
    - Customer Info (card): name, email, phone
    - Items Table: SKU, Product, Qty, Price, Subtotal
    - Order Total (bold, large)
  - Right (40%):
    - Order Status Timeline (vertical):
      - Created ✓
      - Reserved ✓
      - Packed ✓
      - Shipped ← (current, highlighted)
    - Stock Reservation Details:
      - Reserved items count
      - Reserve button (if PENDING)
      - Error message if insufficient stock (red background)
    - Actions:
      - Reserve Stock (if PENDING)
      - View Picklist (if RESERVED)
      - Pack Order (if RESERVED, shows form modal)
      - Generate Label (if PACKED, shows tracking number)
      - Ship Order (if PACKED, requires confirmation)
- Audit trail at bottom: "Created by John on Aug 10, 2:30 PM"

**Pack Order Modal:**
- Title: "Pack Order #ORD-1001"
- Form fields:
  - Packed Weight: number input (lbs)
  - Width: number input (inches)
  - Height: number input (inches)
  - Length: number input (inches)
- Button spacing: Cancel (left), Pack Order (right, primary)

**Picklist View:**
- Table: Item ID, Product, Barcode, Storage Location, Qty, Status
- Print button: (icon top-right)
- Each row shows storage location in prominent badge (e.g., "A-04-12")
- Pick status: unchecked → checked on row click

### TICKETS & ARRIVALS PAGE

**Header Section:**
- Breadcrumb: Dashboard > Tickets
- Title: "Receiving Tickets"
- Quick action: "Log Arrival" (primary button, top-right)

**Filter Bar:**
- Status: PENDING, INSPECTED, STORED, PICKED (checkboxes or tabs)
- Warehouse: dropdown
- Date range: From/To pickers
- Search: by ticket ID

**Tickets Table:**
- Columns:
  - Checkbox
  - Ticket ID (monospace, clickable)
  - Warehouse (12px)
  - Items Count (12px)
  - Status (badge)
  - Arrived Date (12px)
  - Assigned Storage (12px)
  - Manager (if applicable)
  - Actions (3-dot menu)

**Ticket Detail View (click row):**
- Header: "Ticket #RNO-20260813-001" + status badge
- 2-column layout:
  - Left (65%):
    - Shipment Info Card:
      - Tracking Number (copy icon)
      - Carrier
      - Arrived Date/Time
      - No-Ticket Arrival flag (if applicable)
    - Items Checklist Table:
      - Product Image (40x40px thumbnail)
      - Barcode (monospace, copy icon)
      - Product Name (clickable → item detail)
      - Qty
      - Dimensions (W x H)
      - Weight
      - Damage Flag (yellow warning if true)
      - Assigned Storage (badge, e.g., "A-04-12")
      - Status (SCANNED, INSPECTED, STORED)
    - Add Item Button (secondary, below table)
  - Right (35%):
    - Status Timeline:
      - Arrived ✓
      - Inspected ✓ (or current if awaiting)
      - Stored ← (if pending approval)
    - Manager Approval Card (if status is INSPECTED):
      - Message: "Awaiting manager approval"
      - Approve button (primary, green) - MANAGER only
      - Reject button (secondary) - MANAGER only
    - Assign Storage Card:
      - Dropdown: "Select storage location"
      - Assign button (secondary)
    - Audit Trail: timestamp, who created/modified

**Log Item Modal:**
- Title: "Log New Item"
- 2-column form:
  - Left: Form fields
    - Barcode: text input (focus by default, scan barcode)
    - Product Name: text input
    - Width (in): number
    - Height (in): number
    - Weight (lbs): number
    - Damage Flag: checkbox "Mark as Damaged"
    - Damage Notes: textarea (hidden until checkbox)
  - Right: Image preview area
    - "Drag to upload or click" (file upload)
    - Supported: PNG, JPG (max 5MB)
    - Preview thumbnail (200x200px)
- Buttons: Cancel, Add Item (primary)
- On submit: close modal, refresh items table, show success toast

**Log Arrival Modal:**
- Title: "Log New Arrival"
- Form:
  - Warehouse: dropdown (required)
  - Tracking Number: text input (optional)
  - No-Ticket Arrival: checkbox
  - Comments: textarea (optional)
- Buttons: Cancel, Create Ticket (primary)
- On success: show new ticket ID, redirect to detail view

### VOICE PIPELINE PAGE (STAFF)

**Header:**
- Breadcrumb: Dashboard > Voice Pipeline
- Title: "Voice Data Entry"

**Main Layout:**
- 2-column:
  - Left (50%): Recording interface
  - Right (50%): Transcript + parsed data

**Recording Interface Card:**
- Title: "Audio Capture"
- Large recording button (80x80px circle, pulsing animation when recording)
- Status text: "Click to start recording" / "Recording... 00:32" / "Ready to upload"
- Controls below button:
  - Play button (preview recording)
  - Clear button (delete recording)
  - Upload button (disabled if no recording)
- OR file upload section:
  - "Or upload audio file"
  - Drag-drop zone (dashed border, 120px height)
  - File browser button
  - Supported: MP3, WAV, M4A (max 10MB)

**Transcript & Parse Card:**
- Title: "Parsed Data"
- Transcript box:
  - Background: #111827
  - Border: 1px #374151
  - Padding: 16px
  - Text: #F3F4F6, 14px
  - Monospace font
  - Full height, scrollable
- Below: Parsed fields table
  - Columns: Field, Value, Confidence
  - Confidence as progress bar: green (#10B981) for high, yellow for medium, red for low
  - Example rows:
    - Barcode: 012345678905 | 95%
    - Product: Widget A | 88%
    - Weight: 2.5 lbs | 92%
- Action buttons:
  - Confirm button (primary, green) → saves as inventory
  - Discard button (secondary) → clears all
- On confirm: toast "Item logged successfully", clear form

**Confirmation Toast:**
- "Item 012345678905 added to inventory"
- Undo link (15-second window)
- Close button (X)
- Slide up animation from bottom

### USER MANAGEMENT PAGE (OWNER)

**Header:**
- Breadcrumb: Dashboard > Users
- Title: "User Management"
- Button: "Create Manager" (primary, top-right)

**Filter Bar:**
- Role: dropdown (OWNER, MANAGER, STAFF)
- Status: checkbox (Active, Inactive)
- Warehouse: dropdown
- Search: by email or name

**Users Table:**
- Columns:
  - Checkbox
  - Avatar (32x32px, initials on background color per role)
  - Name (14px, bold)
  - Email (12px, #9CA3AF)
  - Role (badge: color-coded)
  - Warehouse (12px)
  - Status (badge: Active = green, Inactive = gray)
  - Created Date (12px)
  - Actions (3-dot menu: Edit, Deactivate, Delete)

**Create Manager Modal:**
- Title: "Create New Manager"
- Form fields:
  - Full Name: text input (required)
  - Email: email input (required, validation)
  - Password: password input (show/hide toggle, requirement indicators below)
  - Password confirmation: password input
  - Warehouse: dropdown (required)
  - Status: radio (Active/Inactive, default Active)
- Password requirements (dynamic checklist):
  - ✓ At least 8 characters
  - ✓ Contains uppercase letter
  - ✓ Contains number
  - ✓ Contains special character
  - Updates as user types
- Buttons: Cancel, Create Manager (primary)

**User Detail/Edit Modal:**
- Show current info
- Editable fields: Full Name, Status
- Non-editable: Email, Role, Created Date
- Actions: Save, Reset Password (secondary), Deactivate (danger)
- Audit info: "Created by Admin on Aug 10, 2:30 PM"

### REPORTS PAGE (OWNER/MANAGER)

**Layout:**
- Breadcrumb: Dashboard > Reports
- Title: "Analytics & Reports"
- Date range picker (top-right): From/To dates
- Export button: dropdown (CSV, XLSX)

**Executive Summary Section:**
- 4 metric cards (same as dashboard):
  - Today's Tickets Created
  - Today's Items Sold
  - Unannounced Arrivals
  - Avg Processing Time
- Sparklines in each card

**Charts Section (2-column grid):**
- Top-left: Order Status Breakdown (donut chart, 300x300px)
- Top-right: Warehouse Comparison (bar chart, 300x300px)
- Bottom-left: Trend Over Time (line chart, warehouse-specific)
- Bottom-right: Inventory Heatmap (per warehouse, color-intensity)

**Stock Totals Table:**
- Title: "Inventory Summary"
- Columns:
  - SKU (monospace)
  - Product Name
  - Warehouse
  - On Hand (quantity)
  - Available (quantity, green text)
  - Reserved (quantity, yellow text)
  - Damaged (quantity, red text)
  - Last Modified (timestamp)
- Sortable columns
- Pagination: 50 rows per page
- Row click → inventory detail view

**Activity Feed:**
- Title: "Recent Activity"
- Timeline view: vertical line with events
- Each event: timestamp (right), event type (left), actor, action
- Filter: by event type (created, updated, deleted)

### WAREHOUSE MANAGEMENT (OWNER only)

**Header:**
- Breadcrumb: Dashboard > Warehouses
- Title: "Warehouse Facilities"
- Button: "Create Warehouse" (primary)

**Warehouses Grid/Table:**
- Grid view: 3 columns
- Card per warehouse:
  - Code (H2, green)
  - Name
  - Address (12px, #9CA3AF)
  - Manager: "John Manager" (if assigned)
  - Stats: 3 badges (Tickets: 45, Items: 230, Storage: 85%)
  - Status: Active/Inactive badge
  - Actions: 3-dot menu (Edit, View Details, Delete)

**Create Warehouse Modal:**
- Form fields:
  - Code: text input (required, 2-3 chars, uppercase auto)
  - Name: text input (required)
  - Address: textarea (optional)
  - Assign Manager: dropdown (optional)
  - Active: toggle (default on)
- Buttons: Cancel, Create Warehouse (primary)

**Warehouse Detail View:**
- Header: Warehouse name + code badge
- Left panel: Info, Manager, Address
- Right panel: Stats (cards)
- Storage Locations Table:
  - Zone, Rack, Bin, Location Code, Occupied?, Capacity
  - Create Location button
- Recent Tickets Table (last 10)
- Edit button: warehouse modal

===========================================
PART 5: INTERACTIONS & ANIMATIONS
===========================================

### PAGE TRANSITIONS
- Fade + slide: 200ms, ease-in-out
- Active page content slides in from right
- Previous page fades out

### HOVER EFFECTS
- All interactive elements: opacity change or background shift
- Smooth 150ms transition
- Cursor: pointer for clickable items
- Disabled items: cursor not-allowed, opacity 50%

### FORM INTERACTIONS
- On input focus: border color → #10B981, shadow glow
- On input error: border color → #EF4444
- On input valid: subtle green checkmark (right-aligned)
- Validation: real-time feedback as typing
- Form submit: button → loading state (spinner inside), disabled

### TABLE INTERACTIONS
- Row hover: background highlight + subtle shadow
- Row click: expand detail or navigate
- Column sort: icon animation (rotate 180° for desc)
- Multi-select: all checkboxes check, "X selected" badge appears
- Drag-to-resize columns: cursor resize on column border

### MODAL INTERACTIONS
- Open: backdrop fade (150ms), modal scale + fade (200ms)
- Close: reverse animation (150ms)
- Form validation: real-time with inline errors
- On submit: button loading state, disable backdrop click

### TOAST NOTIFICATIONS
- Position: bottom-right
- Animation: slide-up + fade (300ms)
- Auto-dismiss: 5 seconds (with progress bar)
- Multiple toasts: stack vertically with 8px spacing
- Hover: pause auto-dismiss
- Close button (X): manual dismiss

### LOADING STATES
- Button: replace text with spinner, disable state
- Page: skeleton loaders in place of content
- Table: rows fade to 50% opacity + skeleton loaders
- Refresh: "Refreshing..." text + spinner icon (rotating)

### SUCCESS/ERROR FEEDBACK
- Success: green toast, checkmark icon, 5s auto-dismiss
- Error: red alert box, stay until user closes
- Warning: yellow alert box, require action or dismiss
- Info: blue toast, informational only

===========================================
PART 6: BACKEND INTEGRATION
===========================================

### API BASE URL
http://127.0.0.1:8000

### AUTHENTICATION HEADERS
- Authorization: Bearer <access_token>
- Content-Type: application/json

### ERROR HANDLING UI
- 400 Bad Request: Show validation errors per field in red
- 401 Unauthorized: Redirect to login, show "Session expired" toast
- 403 Forbidden: Show "Access Denied" alert
- 404 Not Found: Show "Resource not found" message
- 409 Conflict: Show specific error (e.g., "Insufficient stock")
- 500 Server Error: Show generic error with "Retry" button

### PAGINATION IMPLEMENTATION
- Default: 50 items per page
- Show "Showing X-Y of Z results"
- Previous/Next buttons (disabled at bounds)
- Jump to page input
- Rows per page dropdown: 25, 50, 100, 250

===========================================
PART 7: ACCESSIBILITY & PERFORMANCE
===========================================

### ACCESSIBILITY
- WCAG 2.1 AA compliant
- Semantic HTML (nav, main, section, article)
- ARIA labels for icons
- Keyboard navigation: Tab/Shift+Tab, Enter to activate
- Color contrast: 4.5:1 for text, 3:1 for UI components
- Focus states: visible outline on all interactive elements

### PERFORMANCE
- Lazy load images (Intersection Observer)
- Debounce search: 300ms
- Debounce filter changes: 500ms
- Virtualize long tables (show only viewport + buffer)
- Cache API responses: localStorage (1-hour TTL)
- Optimize bundle: tree-shake unused code
- Critical CSS: inline above-the-fold styles

===========================================
PART 8: DEVELOPMENT PRIORITIES
===========================================

**Phase 1 (MVP):**
1. Login page + auth flow
2. Dashboard (basic metrics)
3. Navigation sidebar
4. Orders table + detail view
5. Tickets table + detail view

**Phase 2:**
6. Filters + search
7. Create/Edit modals
8. Voice pipeline page
9. Reports page
10. User management

**Phase 3:**
11. Warehouse management
12. Audit logs
13. Advanced charts
14. Admin settings
15. Polish + animations

===========================================

REFERENCE DESIGN INSPIRATION:
- Inventory app (UI/UX patterns)
- Dark theme with green accent
- Professional enterprise feel
- Data-dense tables with actions
- Clear information hierarchy
- Smooth interactions

START BUILDING WITH:
- React + Tailwind CSS + Headless UI
- OR Vue + Tailwind + Radix Vue
- State: Zustand or Pinia
- HTTP: Axios with interceptors
- Charts: Recharts
- Forms: React Hook Form + Zod
- Icons: Heroicons or Lucide

DESIGN TOKENS:
Export as CSS variables for easy theming:
--color-primary: #10B981
--color-bg-dark: #111827
--color-text-primary: #F3F4F6
[... all colors, sizes, shadows ...]

This project was built with [Lovable](https://lovable.dev).

## Build with Lovable

Continue developing this project in the [Lovable editor](https://lovable.dev/projects/ba1bca33-47ad-482a-a46d-714b515acdef).

- **Ship faster**: describe what you want to build and Lovable handles the code.
- **Stay in sync**: every change made in Lovable is committed straight to this repository.
- **Full ownership**: this code is yours. Push to `main` on GitHub and your changes sync back into Lovable, ready for your next prompt.

## Development

Prefer working locally? You need Node.js and npm — [install with nvm](https://github.com/nvm-sh/nvm#installing-and-updating).

```sh
git clone <this-repository-url>
cd <repository-name>
npm i
npm run dev
```
