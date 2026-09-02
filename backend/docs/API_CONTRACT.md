# Frontend API Contract

This document provides the definitive contract for all ManRakshak Backend v1 API endpoints.

## Base URL
`/api/v1`

## Common Responses
- `401 Unauthorized`: Token missing or invalid.
- `403 Forbidden`: User lacks role permissions or attempting cross-tenant/cross-unit access.
- `404 Not Found`: Resource does not exist or is invisible to the user.
- `422 Unprocessable Entity`: Schema validation failure.
- `429 Too Many Requests`: Rate limit exceeded.

---

## 1. Auth

### POST `/auth/login`
- **Roles**: All
- **Body**: `OAuth2PasswordRequestForm` (form-data: `username` as email, `password`)
- **Response**: `{"access_token": "jwt", "refresh_token": "jwt", "token_type": "bearer"}`

### POST `/auth/refresh`
- **Roles**: All
- **Body**: `{"refresh_token": "jwt"}`
- **Response**: `{"access_token": "jwt", "token_type": "bearer"}`

### POST `/auth/logout`
- **Roles**: All
- **Headers**: `Authorization: Bearer <access_token>`
- **Response**: `{"status": "logged_out"}`

### GET `/auth/me`
- **Roles**: All
- **Headers**: `Authorization: Bearer <access_token>`
- **Response**: User Profile object.

---

## 2. Personnel

### GET `/personnel/me`
- **Roles**: PERSONNEL, WELFARE_OFFICER, COMMANDER
- **Response**: Current personnel profile detail.

### GET `/personnel`
- **Roles**: WELFARE_OFFICER (COMMANDER receives aggregate only via analytics)
- **Query Params**: `unit_id` (optional), `page`, `page_size`
- **Response**: `{"items": [PersonnelProfileList], "total": int}`

### GET `/personnel/{id}`
- **Roles**: WELFARE_OFFICER
- **Response**: `PersonnelProfileDetail` (includes unit mapping)

---

## 3. Wellness

### POST `/wellness/checkins`
- **Roles**: PERSONNEL
- **Body**: 
  ```json
  {
    "physical_score": 1-10,
    "mental_score": 1-10,
    "sleep_hours": 0-24,
    "stress_level": "LOW|MEDIUM|HIGH|SEVERE",
    "notes": "optional"
  }
  ```
- **Response**: `{"id": "...", "status": "submitted"}`

### GET `/wellness/me`
- **Roles**: PERSONNEL
- **Response**: `{"items": [WellnessCheckinSummary]}`

### GET `/wellness/{personnel_id}`
- **Roles**: WELFARE_OFFICER
- **Response**: List of wellness checkins for specific personnel.

---

## 4. Support Requests

### POST `/support`
- **Roles**: PERSONNEL
- **Body**: `{"category": "WORK|PERSONAL|HEALTH|OTHER", "message": "...", "priority": "NORMAL|HIGH|URGENT"}`
- **Response**: Support request object.

### GET `/support/me`
- **Roles**: PERSONNEL
- **Response**: List of own support requests.

### GET `/support/queue`
- **Roles**: WELFARE_OFFICER
- **Query Params**: `status`
- **Response**: Queue of support requests for the organization/unit.

### PUT `/support/{id}/status`
- **Roles**: WELFARE_OFFICER
- **Body**: `{"status": "IN_PROGRESS|RESOLVED|CLOSED", "notes": "optional"}`
- **Response**: Updated support request.

---

## 5. Interventions

### POST `/interventions`
- **Roles**: WELFARE_OFFICER
- **Body**: `{"personnel_id": "...", "action_type": "COUNSELING|MEDICAL|LEAVE|TRAINING", "notes": "...", "follow_up_date": "ISO8601"}`
- **Response**: Created intervention.

### GET `/interventions`
- **Roles**: WELFARE_OFFICER, PERSONNEL (Personnel only sees own)
- **Response**: List of interventions.

### PUT `/interventions/{id}`
- **Roles**: WELFARE_OFFICER
- **Body**: Partial updates to intervention fields.
- **Response**: Updated intervention.

### POST `/interventions/{id}/complete`
- **Roles**: WELFARE_OFFICER
- **Response**: `{"status": "completed"}`

### POST `/interventions/{id}/reschedule`
- **Roles**: WELFARE_OFFICER
- **Body**: `{"follow_up_date": "ISO8601"}`
- **Response**: `{"status": "rescheduled"}`

---

## 6. Notifications

### GET `/notifications`
- **Roles**: All
- **Query**: `is_read`, `page`, `page_size`
- **Response**: List of notifications.

### GET `/notifications/unread-count`
- **Roles**: All
- **Response**: `{"count": int}`

### PUT `/notifications/{id}/read`
- **Roles**: All
- **Response**: `{"status": "success"}`

### PUT `/notifications/read-all`
- **Roles**: All
- **Response**: `{"status": "success"}`

---

## 7. Analytics

### GET `/analytics/wellness`
- **Roles**: COMMANDER, WELFARE_OFFICER
- **Query**: `unit_id`, `start_date`, `end_date`
- **Response**: Aggregate averages and trends. Minimum cohort rules apply.

### GET `/analytics/workload`
- **Roles**: COMMANDER, WELFARE_OFFICER
- **Response**: Support request volume by status and priority.

### GET `/analytics/units`
- **Roles**: COMMANDER
- **Response**: Comparative unit metrics.

---

## 8. Reports & Exports

### GET `/reports/{type}`
- **Roles**: COMMANDER, WELFARE_OFFICER
- **Path Param**: `type` = `wellness`, `workload`, `units`, `welfare-activity`
- **Response**: Structured JSON report with metadata.

### GET `/reports/{type}/export`
- **Roles**: COMMANDER, WELFARE_OFFICER
- **Query**: `format=csv|json`
- **Response**: Streamed file download.

---

## 9. Administrator 

*(All endpoints require `ADMINISTRATOR` role)*

- `GET /admin/organization` - Current org details
- `PUT /admin/organization` - Update org settings
- `POST /admin/units` - Create a new unit
- `POST /admin/users` - Create a new user (with role)
- `GET /admin/users` - List all users in org
- `GET /admin/settings` - Checkin frequency settings
- `PUT /admin/settings` - Update settings
- `GET /admin/audit` - View security audit logs
