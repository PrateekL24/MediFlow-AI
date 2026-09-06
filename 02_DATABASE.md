# MediFlow AI — Database Design

## 1. Purpose

The MediFlow AI database stores the persistent information required to operate the healthcare administration assistant.

The database is responsible for:

- Patient records
- Doctor and department information
- Appointment availability
- Booked appointments
- Workflow persistence
- Audit events
- Uploaded documents
- Escalations
- Reminders
- Application users

The database is implemented using Supabase/PostgreSQL.

The application follows this responsibility boundary:

Agent
→ Tool
→ Service
→ Repository
→ Supabase

Agents and services must not directly query Supabase.

Repositories are the only layer responsible for database access.

---

# 2. Database Tables

Current public tables:

1. `patients`
2. `departments`
3. `doctors`
4. `appointment_slots`
5. `appointments`
6. `workflow_runs`
7. `audit_events`
8. `documents`
9. `escalations`
10. `reminders`
11. `users`

---

# 3. Patients

## Table

`patients`

## Purpose

Stores patient demographic and contact information.

## Fields

| Column        | Type      | Purpose                   |
| ------------- | --------- | ------------------------- |
| `patient_id`  | UUID      | Unique patient identifier |
| `first_name`  | varchar   | Patient first name        |
| `last_name`   | varchar   | Patient last name         |
| `gender`      | varchar   | Patient gender            |
| `age`         | int       | Patient age               |
| `blood_group` | varchar   | Blood group               |
| `phone`       | varchar   | Mobile/contact number     |
| `email`       | varchar   | Email address             |
| `address`     | text      | Patient address           |
| `created_at`  | timestamp | Record creation time      |

## Important Design Decision

`phone` is **not a unique identifier**.

Multiple patients may share the same mobile number.

Example:

```text
Phone: 9876543210

Patient 1 → Rahul Sharma → Age 42
Patient 2 → Ananya Sharma → Age 16
Patient 3 → Priya Sharma → Age 38

Therefore patient identification must support:

Search by phone
        ↓
0 matches → registration
1 match  → continue
N matches → ask user to select patient

The system must never assume that a phone number uniquely identifies a patient.

4. Departments
Table

departments

Purpose

Stores hospital departments/specializations.

Fields
Column	Type	Purpose
department_id	UUID	Unique department identifier
department_name	varchar	Department name
description	text	Department description
Relationship
departments
    │
    └── doctors

A department can have multiple doctors.

5. Doctors
Table

doctors

Purpose

Stores doctor information used for doctor search, recommendations, fees, and availability.

Fields
Column	Type	Purpose
doctor_id	UUID	Unique doctor identifier
doctor_name	varchar	Doctor name
department_id	UUID	Associated department
specialization	varchar	Medical specialization
experience_years	int	Years of experience
available_days	text	General working days
available_time	text	General working hours
consultation_fee	int	Consultation fee
status	varchar	Doctor availability/status
Relationship
departments
     │
     └── doctors

The doctor record provides general availability information.

Actual appointment booking availability should come from:

appointment_slots

rather than assuming that available_days and available_time represent a specific bookable slot.

6. Appointment Slots
Table

appointment_slots

Purpose

Stores actual bookable time slots for doctors.

Fields
Column	Type	Purpose
slot_id	UUID	Unique slot identifier
doctor_id	UUID	Doctor associated with slot
start_time	timestamp	Slot start
end_time	timestamp	Slot end
status	text	Slot availability
created_at	timestamp	Creation time
Relationship
doctors
    │
    └── appointment_slots
Slot Lifecycle

Typical states:

available
    ↓
selected
    ↓
booked

The exact implementation of slot reservation/locking may evolve.

Important Design Principle

Availability must be checked independently from patient identification.

Correct flow:

Doctor
  ↓
Date
  ↓
Available slots
  ↓
User selects slot
  ↓
Patient identification
  ↓
Confirmation
  ↓
Booking

A user should not need to provide their mobile number merely to see available slots.

7. Appointments
Table

appointments

Purpose

Stores confirmed/booked appointments.

Fields
Column	Type	Purpose
appointment_id	UUID	Unique appointment identifier
patient_id	UUID	Patient
doctor_id	UUID	Doctor
appointment_date	date	Appointment date
appointment_time	time	Appointment time
symptoms	text	Symptoms/reason for visit
status	varchar	Appointment status
created_at	timestamp	Creation time
Relationships
patients
    │
    └── appointments
             │
             └── doctors
Current Status

The application currently creates appointments with:

Booked

Additional lifecycle states may be introduced later if required, for example:

Booked
Confirmed
Completed
Cancelled
No-show

These should only be added when the workflow actually requires them.

8. Appointment Booking Integrity

Appointment booking must prevent duplicate bookings.

Current service-level flow:

User selects slot
        ↓
Check existing appointment
        ↓
If already booked
        ↓
Reject booking
        ↓
Ask user to select another slot

The application currently checks:

doctor_id
appointment_date
appointment_time

before creating an appointment.

Future Hardening

Application-level checks alone are not sufficient for production concurrency.

Two requests could theoretically perform:

Request A → check slot → available
Request B → check slot → available

Request A → insert
Request B → insert

Therefore production hardening should introduce a database-level uniqueness constraint or transactional booking mechanism.

The exact constraint should be designed around the final slot-booking model before implementation.

9. Workflow Runs
Table

workflow_runs

Purpose

Persists the state of an active or completed MediFlow workflow.

This allows the system to survive:

Streamlit reruns
user follow-up messages
interrupted workflows
application restarts
future API-based clients
Fields
Column	Type	Purpose
workflow_id	UUID	Unique workflow identifier
session_id	text	Conversation/session identifier
current_agent	text	Current/responsible agent
current_node	text	Current workflow graph node
workflow_state	jsonb	Persisted workflow state
status	text	Workflow lifecycle status
created_at	timestamp	Creation time
updated_at	timestamp	Last update
Database Status Values

The database currently supports:

running
completed
failed
paused

Application-level workflow states are mapped to these values.

started          → running
in_progress      → running
waiting_for_user → paused
completed        → completed
failed           → failed
Why JSONB?

workflow_state contains dynamic conversational state such as:

intent
patient information
selected patient
selected doctor
doctors found
appointment information
awaiting input
next step
error information

The workflow state is therefore stored as JSONB rather than spreading transient workflow fields across many database columns.

Important Security Consideration

The current implementation may persist patient information inside workflow_state.

This is acceptable for the current development stage but should be reviewed during the security/privacy hardening phase.

The production design should minimize unnecessary PHI stored in workflow state.

10. Audit Events
Table

audit_events

Purpose

Provides an audit trail of important actions performed during workflows.

Fields
Column	Type	Purpose
audit_id	UUID	Unique audit event
workflow_id	UUID	Associated workflow
agent_name	text	Agent responsible
tool_name	text	Tool involved
action	text	Action performed
status	text	Action result
metadata	jsonb	Additional event information
created_at	timestamp	Event time
Example

A patient registration could produce an event similar to:

workflow_id: ...
agent_name: Registration
tool_name: PatientTool
action: create_patient
status: success
Audit Principle

Audit logging should capture meaningful business actions.

It should not blindly store complete conversation transcripts or unnecessary sensitive patient information.

11. Documents
Table

documents

Purpose

Stores metadata about patient documents.

Fields
Column	Type	Purpose
document_id	UUID	Unique document identifier
patient_id	UUID	Patient associated with document
document_name	varchar	Document name
document_type	varchar	Document category
file_path	text	Storage path/reference
uploaded_at	timestamp	Upload time
Relationship
patients
    │
    └── documents

The database should store document metadata.

The actual file should be stored in appropriate secure object storage rather than directly inside PostgreSQL.

12. Escalations
Table

escalations

Purpose

Stores situations that require human intervention.

Examples may include:

unresolved workflow
safety concern
unsupported request
operational exception
manual review requirement
Fields
Column	Type	Purpose
escalation_id	UUID	Unique escalation
workflow_id	UUID	Associated workflow
patient_id	UUID	Related patient
reason	text	Reason for escalation
status	text	Escalation status
assigned_to	UUID	Assigned user
created_at	timestamp	Creation time
resolved_at	timestamp	Resolution time
Typical Lifecycle
pending
   ↓
assigned
   ↓
resolved

The exact lifecycle can be expanded when the human-escalation workflow is implemented.

13. Reminders
Table

reminders

Purpose

Stores reminders associated with patients and appointments.

Fields
Column	Type	Purpose
reminder_id	UUID	Unique reminder
patient_id	UUID	Patient
appointment_id	UUID	Related appointment
reminder_type	text	Type of reminder
reminder_time	timestamp	Scheduled reminder time
status	text	Reminder status
created_at	timestamp	Creation time
Relationship
patients
    │
    └── reminders
             │
             └── appointments

Reminder execution is a separate concern from appointment booking.

Booking an appointment may create a reminder, but the reminder delivery mechanism should not be implemented inside the AppointmentAgent.

14. Users
Table

users

Purpose

Represents application/hospital users who may interact with administrative workflows or receive escalations.

Fields
Column	Type	Purpose
id	UUID	User identifier
full_name	text	User name
email	text	User email
role	text	User role
created_at	timestamp	Creation time
updated_at	timestamp	Last update

Potential roles include administrative or clinical staff roles.

The exact authorization model will be defined during the security hardening phase.

15. High-Level Relationships

Current logical database relationship:

                    ┌──────────────┐
                    │ Departments  │
                    └──────┬───────┘
                           │
                           │
                    ┌──────▼───────┐
                    │   Doctors    │
                    └──────┬───────┘
                           │
              ┌────────────┴────────────┐
              │                         │
      ┌───────▼────────┐       ┌────────▼────────┐
      │ Appointment    │       │ Appointment     │
      │ Slots          │       │ Records         │
      └────────────────┘       └────────┬────────┘
                                        │
                              ┌─────────┴─────────┐
                              │                   │
                       ┌──────▼──────┐     ┌──────▼──────┐
                       │  Patients   │     │  Reminders  │
                       └──────┬──────┘     └─────────────┘
                              │
                    ┌─────────┼─────────┐
                    │         │         │
             ┌──────▼─────┐ ┌─▼──────┐ ┌▼────────────┐
             │ Documents  │ │Audits  │ │ Escalations │
             └────────────┘ └────────┘ └─────────────┘


                    ┌─────────────────┐
                    │ Workflow Runs   │
                    │                 │
                    │ session         │
                    │ workflow state  │
                    │ lifecycle       │
                    └─────────────────┘

workflow_runs is related conceptually to all workflow-driven operations through workflow_id.

16. Database vs Application Responsibilities

The application and database should not duplicate responsibilities unnecessarily.

Repository

Responsible for:

SELECT
INSERT
UPDATE
DELETE
filtering
ordering
database-specific queries

Example:

AppointmentRepository
        ↓
Supabase
Service

Responsible for:

validation
business rules
workflow-level decisions
interpreting repository results

Example:

AppointmentService
        ↓
validate booking
        ↓
check existing appointment
        ↓
create appointment
Agent

Responsible for:

understanding user intent
deciding what workflow step is required
asking for missing information
presenting results conversationally

Agents should not contain raw SQL or Supabase queries.

17. Data Ownership

Each table has a primary business owner:

Table	Primary Responsibility
patients	Patient records
departments	Department information
doctors	Doctor information
appointment_slots	Bookable availability
appointments	Confirmed appointments
workflow_runs	Workflow persistence
audit_events	Audit trail
documents	Patient document metadata
escalations	Human escalation
reminders	Reminder scheduling
users	Application users
18. Security and Privacy Principles

MediFlow AI handles healthcare-related information.

Database design must therefore follow least-privilege principles.

Important requirements:

Do not expose database credentials to the frontend.
Do not expose Supabase service-role credentials to users.
Keep secrets in environment variables.
Avoid unnecessary PHI in logs.
Avoid unnecessary PHI in audit metadata.
Minimize PHI stored in workflow state.
Restrict access to patient records.
Validate all user-controlled inputs.
Apply authorization before sensitive operations.
Use database constraints for important integrity rules.
Enable and properly configure Row Level Security where appropriate.

Security hardening is a separate implementation phase and should not be mixed into unrelated feature changes.

19. Future Database Hardening

The current schema is sufficient for the core workflow, but production hardening should review:

Constraints

Examples:

appointments
→ prevent duplicate doctor/date/time bookings

patients
→ validate required fields

appointment_slots
→ validate valid status values
Indexes

Likely useful indexes include:

patients.phone
doctors.doctor_name
appointment_slots.doctor_id + start_time
appointments.doctor_id + appointment_date + appointment_time
workflow_runs.session_id
workflow_runs.status
audit_events.workflow_id
documents.patient_id

Indexes should be added based on actual query patterns rather than blindly indexing every column.

Row Level Security

RLS policies should define who can:

read patient records
create appointments
view documents
create/view escalations
access workflow data
Concurrency

Appointment booking should eventually use database-level protection against race conditions.

20. Important Architectural Decisions
Decision 1 — Phone is not unique

A mobile number may belong to multiple patients.

Therefore:

phone → patient lookup

is a discovery mechanism, not a unique identity mechanism.

Decision 2 — Appointment availability is separate from patient identification

A user can ask:

"What slots are available tomorrow?"

without identifying a patient.

Patient identification begins when the user moves toward actually booking a slot.

Decision 3 — Workflow state is persisted

Long-running conversational workflows cannot rely only on in-memory Streamlit state.

workflow_runs provides persistent workflow state.

Decision 4 — Agents do not access Supabase directly

The dependency direction remains:

Agent
  ↓
Tool
  ↓
Service
  ↓
Repository
  ↓
Supabase

This keeps business logic testable and prevents database concerns from leaking into agents.

Decision 5 — Actual slots are different from doctor availability

Doctor records provide general working information.

appointment_slots represents concrete bookable times.

Therefore the booking system should use actual slots when available rather than generating booking times purely from:

available_days
available_time
21. Current Database Maturity

The current database is suitable for:

development
workflow testing
hackathon demonstration
core appointment workflows

Before production deployment, it requires additional work around:

RLS
authorization
database constraints
concurrency-safe booking
indexes
PHI minimization
audit policy
document storage security
retention policies
migration management
backup/recovery
observability

These are intentionally treated as separate hardening tasks rather than mixing them into the core feature implementation.

22. Source of Truth

The application code is maintained in GitHub.

The database schema and migration definitions should eventually also be version-controlled.

Database changes should follow:

Design
  ↓
Migration
  ↓
Apply locally/test environment
  ↓
Test
  ↓
Commit
  ↓
Push GitHub

Manual production-only schema changes should be avoided.

23. Summary

MediFlow AI uses Supabase/PostgreSQL as its persistent data layer.

The database separates:

Patient data
Doctor data
Appointment availability
Booked appointments
Workflow state
Audit events
Documents
Escalations
Reminders
Users

The most important workflow-related distinction is:

Doctor availability
        ≠
Patient identification
        ≠
Appointment booking

These concerns must remain separate in both the database and application architecture.

The database provides persistence and integrity.

Services provide business rules.

Tools provide controlled access.

Agents make workflow decisions.
```
