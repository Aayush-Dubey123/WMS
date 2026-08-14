# Whitfield WMS Frontend - Comprehensive Test Plan

**Created**: 2026-08-13  
**Purpose**: Systematic testing of all frontend functionality  
**Status**: Ready for execution

---

## 📋 PRE-TEST CHECKLIST

Before starting tests, verify:

- [ ] Backend running: `http://127.0.0.1:8000`
- [ ] Frontend running: `http://localhost:5173`
- [ ] MongoDB connected
- [ ] Browser console open (F12) for error tracking
- [ ] Network tab open to monitor API calls

---

## 🧪 TEST SUITE 1: LOGIN & AUTHENTICATION

### Test 1.1: Login Page Loads
**Steps:**
1. Navigate to `http://localhost:5173/login`
2. Verify page displays:
   - Whitfield WMS branding
   - "Quick Demo" and "Sign In" tabs
   - 3 demo role buttons (OWNER, MANAGER, STAFF)

**Expected Result:** ✅ Login page displays correctly

**Pass/Fail:** ___

---

### Test 1.2: Demo Login - OWNER Role
**Steps:**
1. On login page, click "OWNER" button
2. Verify button fills form fields with:
   - Email: `owner@whitfield.com`
   - Password: `OwnerPass123!`
3. Click "Sign In with Demo" button
4. Verify redirect to dashboard

**Expected Result:** ✅ Logged in as OWNER, dashboard loads

**Pass/Fail:** ___

---

### Test 1.3: Demo Login - MANAGER Role
**Steps:**
1. Logout (click user menu → Log out)
2. Go back to login
3. Click "MANAGER" button
4. Click "Sign In with Demo"

**Expected Result:** ✅ Logged in as MANAGER, dashboard loads

**Pass/Fail:** ___

---

### Test 1.4: Demo Login - STAFF Role
**Steps:**
1. Logout
2. Go back to login
3. Click "STAFF" button
4. Click "Sign In with Demo"

**Expected Result:** ✅ Logged in as STAFF, dashboard loads

**Pass/Fail:** ___

---

### Test 1.5: Already Authenticated Redirect
**Steps:**
1. While logged in, manually navigate to `/login`

**Expected Result:** ✅ Redirect to dashboard immediately

**Pass/Fail:** ___

---

### Test 1.6: Manual Login (Sign In Tab)
**Steps:**
1. Logout
2. Click "Sign In" tab
3. Enter email: `owner@whitfield.com`
4. Enter password: `OwnerPass123!`
5. Click "Sign In"

**Expected Result:** ✅ Login successful, redirected to dashboard

**Pass/Fail:** ___

---

### Test 1.7: Invalid Credentials
**Steps:**
1. On Sign In tab, enter:
   - Email: `invalid@test.com`
   - Password: `wrongpass`
2. Click "Sign In"

**Expected Result:** ✅ Error toast: "Invalid credentials" or similar

**Pass/Fail:** ___

---

## 🎯 TEST SUITE 2: ROLE-BASED NAVIGATION

### Test 2.1: OWNER Navigation
**Steps:**
1. Login as OWNER
2. Check sidebar menu for items

**Expected Result:** ✅ OWNER sees all menu items:
- Dashboard
- Orders & Fulfillment
- Tickets & Arrivals
- Voice Pipeline
- Reports
- User Management
- Warehouses

**Pass/Fail:** ___

---

### Test 2.2: MANAGER Navigation
**Steps:**
1. Login as MANAGER
2. Check sidebar menu

**Expected Result:** ✅ MANAGER sees (NO Warehouses):
- Dashboard
- Orders & Fulfillment
- Tickets & Arrivals
- Voice Pipeline
- Reports
- User Management

**Pass/Fail:** ___

---

### Test 2.3: STAFF Navigation
**Steps:**
1. Login as STAFF
2. Check sidebar menu

**Expected Result:** ✅ STAFF sees only:
- Dashboard
- Orders & Fulfillment
- Tickets & Arrivals
- Voice Pipeline

**Pass/Fail:** ___

---

## 📊 TEST SUITE 3: DASHBOARD

### Test 3.1: Dashboard Loads with Real Data
**Steps:**
1. Login as OWNER
2. Navigate to Dashboard (home)
3. Observe metric cards and charts

**Expected Result:** ✅ Dashboard loads without errors:
- 4 metric cards show values (not NaN or undefined)
- Charts render properly
- Recent arrivals table shows data or "No arrivals" message
- Recent orders table shows data or "No orders" message

**Pass/Fail:** ___

---

### Test 3.2: Dashboard API Calls
**Steps:**
1. Open Network tab (F12)
2. Refresh dashboard
3. Look for API calls

**Expected Result:** ✅ Should see calls to:
- `/reports/summary` (200 OK)
- `/reports/arrived-today` (200 OK)
- `/orders` (200 OK)
- `/tickets` (200 OK)
- `/approvals` (200 OK if MANAGER)

**Pass/Fail:** ___

**Notes:** Record actual response times

---

### Test 3.3: User Profile Card on Dashboard
**Steps:**
1. On dashboard, find "Account" card
2. Verify it shows:
   - User name
   - Email
   - Role (OWNER/MANAGER/STAFF)
   - Facility (if assigned)

**Expected Result:** ✅ Profile information displays correctly

**Pass/Fail:** ___

---

### Test 3.4: Manager Approval Alert
**Steps:**
1. Login as MANAGER
2. Go to dashboard
3. Check for "pending approval" alert/section

**Expected Result:** ✅ If approvals exist, alert shows count. Otherwise shows "No pending approvals"

**Pass/Fail:** ___

---

### Test 3.5: Dashboard Responsiveness
**Steps:**
1. On dashboard, resize window to mobile (< 768px)
2. Check layout

**Expected Result:** ✅ Layout adapts:
- Cards stack vertically
- Tables become horizontally scrollable
- Navigation collapses to hamburger menu

**Pass/Fail:** ___

---

## 📦 TEST SUITE 4: ORDERS PAGE

### Test 4.1: Orders List Loads
**Steps:**
1. Click "Orders & Fulfillment" in sidebar
2. Wait for page to load

**Expected Result:** ✅ Orders page loads with:
- Search field
- Status filter buttons (ALL, PENDING, RESERVED, PACKED, SHIPPED)
- Table with orders (or "No orders found")

**Pass/Fail:** ___

---

### Test 4.2: Create Order Dialog Opens
**Steps:**
1. On Orders page, click "+ Create Order" button
2. Dialog should appear

**Expected Result:** ✅ Dialog displays with fields:
- Order ID
- Customer Name
- Warehouse

**Pass/Fail:** ___

---

### Test 4.3: Create Order (Successful)
**Steps:**
1. Open create dialog
2. Fill in:
   - Order ID: `TEST-001`
   - Customer Name: `Test Customer`
   - Warehouse: `6a7de31233056991c541a004` (or valid warehouse ID)
3. Click "Create Order"

**Expected Result:** ✅ 
- Loading spinner shows
- Success toast appears
- Dialog closes
- New order appears in list

**Pass/Fail:** ___

---

### Test 4.4: Create Order (Missing Fields)
**Steps:**
1. Open create dialog
2. Leave fields empty
3. Click "Create Order"

**Expected Result:** ✅ Validation error shows (required fields)

**Pass/Fail:** ___

---

### Test 4.5: Filter Orders by Status
**Steps:**
1. On Orders page, click "PENDING" status filter
2. Table updates

**Expected Result:** ✅ Only PENDING orders show in table

**Pass/Fail:** ___

**Repeat for:** RESERVED, PACKED, SHIPPED

---

### Test 4.6: Search Orders
**Steps:**
1. On Orders page, search field
2. Type an order ID or customer name
3. Table filters

**Expected Result:** ✅ Table shows matching orders

**Pass/Fail:** ___

---

## 🔐 TEST SUITE 5: ERROR HANDLING & EDGE CASES

### Test 5.1: Network Error (Offline)
**Steps:**
1. Open DevTools Network tab
2. Set throttling to "Offline"
3. Navigate to dashboard or orders page

**Expected Result:** ✅ Error message shows, page doesn't crash

**Pass/Fail:** ___

---

### Test 5.2: 401 Unauthorized (Expired Token)
**Steps:**
1. Login successfully
2. Go to browser DevTools → Application → localStorage
3. Delete the `access_token` entry
4. Try to navigate to `/orders`

**Expected Result:** ✅ Redirect to login page

**Pass/Fail:** ___

---

### Test 5.3: 403 Forbidden (Insufficient Permissions)
**Steps:**
1. Login as STAFF
2. Try to manually navigate to `/warehouses` (OWNER only)

**Expected Result:** ✅ Redirect to dashboard or show error

**Pass/Fail:** ___

---

### Test 5.4: Browser Console - No Errors
**Steps:**
1. Open DevTools Console
2. Navigate through app (login → dashboard → orders → etc.)
3. Check for errors

**Expected Result:** ✅ No red error messages in console
- Warnings are OK
- Errors = FAIL

**Pass/Fail:** ___

---

## ⚡ TEST SUITE 6: PERFORMANCE & LOAD TIME

### Test 6.1: Initial Page Load Time
**Steps:**
1. Open DevTools Performance tab
2. Navigate to `http://localhost:5173`
3. Let page fully load
4. Record time to interactive

**Expected Result:** ✅ Load time < 3 seconds

**Actual Time:** ___ seconds

**Pass/Fail:** ___

---

### Test 6.2: Dashboard Load Time (Authenticated)
**Steps:**
1. Clear DevTools
2. Login (if not already)
3. Refresh dashboard
4. Measure load time

**Expected Result:** ✅ < 2 seconds

**Actual Time:** ___ seconds

**Pass/Fail:** ___

---

### Test 6.3: Orders Page Load Time
**Steps:**
1. Clear DevTools
2. Click "Orders & Fulfillment"
3. Measure time to table display

**Expected Result:** ✅ < 2 seconds

**Actual Time:** ___ seconds

**Pass/Fail:** ___

---

### Test 6.4: Memory Leaks (Extended Session)
**Steps:**
1. Open DevTools Memory tab
2. Record baseline memory usage
3. Navigate: Dashboard → Orders → Dashboard → Orders (5 times)
4. Record final memory usage

**Expected Result:** ✅ Memory doesn't increase more than 20MB

**Baseline:** ___ MB  
**Final:** ___ MB  
**Delta:** ___ MB

**Pass/Fail:** ___

---

## 📝 TEST SUITE 7: FORM VALIDATION & UX

### Test 7.1: Email Validation
**Steps:**
1. On Login page, Sign In tab
2. Enter email: `invalid-email`
3. Try to submit

**Expected Result:** ✅ Error: "Invalid email address"

**Pass/Fail:** ___

---

### Test 7.2: Required Fields
**Steps:**
1. On Create Order dialog
2. Leave required fields empty
3. Try to submit

**Expected Result:** ✅ Error messages appear for empty fields

**Pass/Fail:** ___

---

### Test 7.3: Toast Notifications
**Steps:**
1. Perform any successful action (login, create order)
2. Observe notification in bottom right

**Expected Result:** ✅ Toast appears with message

**Pass/Fail:** ___

---

### Test 7.4: Loading States
**Steps:**
1. On Create Order dialog
2. Click "Create Order"
3. Observe button state

**Expected Result:** ✅ Button shows spinner + "Creating..." text

**Pass/Fail:** ___

---

## 🗂️ API RESPONSE VERIFICATION

### Test 8.1: Verify API Response Structure
**Steps:**
1. Open DevTools Network tab
2. Login
3. Click on API call (e.g., `/reports/summary`)
4. Check Response tab
5. Verify structure matches backend schema

**Expected Result:** ✅ Response contains expected fields

**Sample Response:**
```json
{
  "todays_tickets": 5,
  "todays_stored": 12,
  "pending_approvals": 2,
  "todays_sold": 3
}
```

**Pass/Fail:** ___

---

### Test 8.2: Verify Token in Headers
**Steps:**
1. Open DevTools Network tab
2. Click any API call
3. Go to "Request Headers"
4. Look for: `Authorization: Bearer eyJ...`

**Expected Result:** ✅ Bearer token present in Authorization header

**Pass/Fail:** ___

---

## 📊 TEST SUMMARY

| Test Suite | Passed | Failed | Total |
|-----------|--------|--------|-------|
| 1. Authentication | ___ | ___ | 7 |
| 2. Navigation | ___ | ___ | 3 |
| 3. Dashboard | ___ | ___ | 5 |
| 4. Orders | ___ | ___ | 6 |
| 5. Error Handling | ___ | ___ | 4 |
| 6. Performance | ___ | ___ | 4 |
| 7. Form Validation | ___ | ___ | 4 |
| 8. API Verification | ___ | ___ | 2 |
| **TOTAL** | ___ | ___ | **35** |

---

## 🔴 KNOWN ISSUES (If Any)

Issue #1: ___________________________________  
Status: [ ] Not reproduced [ ] Reproduced [ ] Fixed  
Steps: _________________________________

Issue #2: ___________________________________  
Status: [ ] Not reproduced [ ] Reproduced [ ] Fixed  
Steps: _________________________________

---

## ✅ SIGN-OFF

- **Tested By:** _______________________
- **Date:** _______________________
- **Overall Result:** [ ] PASS [ ] FAIL
- **Notes:** _________________________________

---

## 📝 FEEDBACK & SUGGESTIONS

Performance Improvements Needed:
- ______________________________________
- ______________________________________

UI/UX Improvements:
- ______________________________________
- ______________________________________

Missing Features:
- ______________________________________
- ______________________________________

---

**Next Steps:**
1. Complete all 35 tests
2. Document any failures
3. Build remaining pages (Tickets, Users, Reports, Voice, Warehouses)
4. Re-run test suite
5. Performance optimization if needed
