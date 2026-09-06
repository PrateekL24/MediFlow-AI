# MediFlow AI — Workflow Design

## 1. Purpose

MediFlow AI is a conversational healthcare administration assistant.

The workflow layer is responsible for coordinating agents and maintaining the state of multi-step interactions.

The workflow must allow the user to provide information over multiple messages without restarting the process.

The core architecture is:

Agent
→ Tool
→ Service
→ Repository
→ Supabase

The workflow layer connects the agents and controls the sequence in which they operate.

---

# 2. Workflow Principles

The workflow system follows these principles:

1. Agents make decisions.
2. Tools provide controlled access to backend capabilities.
3. Services contain business logic.
4. Repositories handle database access.
5. Workflow state persists across user messages.
6. The system asks for missing information instead of guessing.
7. Availability and booking are separate operations.
8. Patient identity must be verified before patient-specific actions.
9. Important workflow actions should be auditable.
10. A workflow can pause and resume.

---

# 3. High-Level Workflow Architecture

```text
User
 │
 ▼
Streamlit / API
 │
 ▼
WorkflowRunner
 │
 ▼
LangGraph Workflow
 │
 ▼
Supervisor
 │
 ├── Reception
 │
 ├── Registration
 │
 ├── Doctor
 │
 └── Appointment
 │
 ▼
Tools
 │
 ▼
Services
 │
 ▼
Repositories
 │
 ▼
Supabase
```

The Supervisor decides which specialized workflow should handle the request.

---

# 4. Agents

Current agents:

- Supervisor
- Reception
- Registration
- Doctor
- Appointment

Each agent has a specific responsibility.

## Supervisor

Responsible for:

- understanding user intent
- extracting explicitly provided information
- selecting the appropriate workflow
- resolving direct references using available state

The Supervisor must not perform database actions.

---

## Reception

Responsible for:

- patient identification
- collecting patient contact information
- searching for existing patients
- handling multiple patients sharing a phone number
- directing new patients to registration

Reception does not create patient records directly.

It uses:

```text
Reception Agent
→ PatientTool
→ PatientService
→ PatientRepository
→ Supabase
```

---

## Registration

Responsible for:

- collecting required registration information
- validating registration input
- creating a new patient record
- selecting the newly created patient

Registration does not directly access Supabase.

---

## Doctor

Responsible for:

- doctor search
- doctor recommendation
- doctor fee information
- doctor availability information
- identifying the doctor relevant to an appointment request

Doctor availability and actual appointment slots are separate concepts.

---

## Appointment

Responsible for:

- appointment availability
- slot selection
- appointment-specific information
- booking confirmation
- appointment creation

The Appointment Agent must not assume that saying:

```text
"I want to book an appointment"
```

means that the user has already selected a slot or confirmed the booking.

---

# 5. Supervisor Workflow

The Supervisor receives every new request unless the workflow is already waiting for a specific input.

Example:

```text
User:
"What is the consultation fee for Dr. Ritu Shah?"

        ↓

Supervisor

        ↓

intent = doctor_fee
doctor_name = Dr. Ritu Shah

        ↓

Doctor Agent
```

The Supervisor should extract only information provided by the user or information that can be directly resolved from workflow context.

It must not invent:

- patient details
- doctor details
- appointment dates
- appointment times
- symptoms
- confirmation

---

# 6. Patient Identification Workflow

Patient identification is required before patient-specific actions such as booking an appointment.

The system must verify the patient through the database.

The system must not trust statements such as:

```text
"I am an existing patient."
```

or:

```text
"I am a new patient."
```

The database is the source of truth.

---

## Patient Identification Flow

```text
Ask for mobile number
        ↓
Validate mobile number
        ↓
Search patients by phone
        ↓
 ┌───────────────┬────────────────┬──────────────────┐
 │               │                │
0 matches     1 match          Multiple matches
 │               │                │
 ▼               ▼                ▼
Registration   Continue       Ask user to select
                              the correct patient
```

---

# 7. Shared Phone Numbers

Phone numbers are not unique patient identifiers.

Example:

```text
9876543210

1. Rahul Sharma — Age 42
2. Ananya Sharma — Age 16
3. Priya Sharma — Age 38
```

The system must ask which patient is visiting.

The user can identify the patient using:

- number
- name
- another supported selection format

The selected patient must then be stored in:

```text
selected_patient
```

---

# 8. New Patient Workflow

When no patient is found:

```text
Phone number
    ↓
No patient found
    ↓
Registration
    ↓
Collect required information
    ↓
Create patient
    ↓
Select created patient
    ↓
Continue original workflow
```

If the original request was an appointment booking request, registration should return control to the appointment workflow.

Example:

```text
User:
"I want to book an appointment."

        ↓

Appointment workflow

        ↓

Patient identification

        ↓

No patient found

        ↓

Registration

        ↓

Patient created

        ↓

Return to appointment workflow
```

The user should not have to restart the appointment request.

---

# 9. Appointment Workflow

Appointment booking is a multi-stage workflow.

The target design is:

```text
Availability
    ↓
Slot Selection
    ↓
Patient Identification
    ↓
Confirmation
    ↓
Booking
```

This separation is important.

A user should be able to view available slots without providing their mobile number.

---

# 10. Appointment Availability

Availability is doctor/date specific.

Example:

```text
User:
"What slots are available for Dr. Ritu Shah tomorrow?"
```

The system should:

```text
Identify doctor
    ↓
Identify date
    ↓
Query appointment_slots
    ↓
Return available slots
```

Patient identification is not required at this stage.

---

# 11. Slot Selection

After available slots are displayed, the user selects one.

Example:

```text
Available slots:

1. 09:30 AM
2. 10:30 AM
3. 11:30 AM
4. 02:00 PM

User:
"I want 10:30 AM."
```

The workflow stores the selected slot.

Example state:

```text
appointment_data:
    doctor_id
    appointment_date
    appointment_time
    slot_id
```

The workflow then moves to patient identification.

---

# 12. Patient Identification After Slot Selection

The correct sequence is:

```text
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
```

This avoids asking for personal information before it is necessary.

---

# 13. Direct Booking Requests

The system should support requests that contain appointment information immediately.

Example:

```text
"Book Dr. Ritu Shah tomorrow."
```

The workflow should:

```text
Identify doctor
    ↓
Identify date
    ↓
Show available slots
    ↓
Wait for slot selection
```

It must not immediately create an appointment.

Another example:

```text
"Book Dr. Ritu Shah tomorrow at 10:30 AM."
```

The system can identify:

```text
doctor = Dr. Ritu Shah
date = tomorrow
time = 10:30 AM
```

It should verify that the requested slot is available.

If available:

```text
Requested slot
    ↓
Patient identification
    ↓
Confirmation
    ↓
Booking
```

If unavailable:

```text
Requested slot unavailable
    ↓
Show available alternatives
    ↓
Wait for user selection
```

---

# 14. Booking Confirmation

Selecting a slot does not necessarily mean the user has confirmed the final booking.

The workflow should clearly distinguish:

```text
slot selected
```

from:

```text
booking confirmed
```

Example:

```text
Selected appointment:

Doctor: Dr. Ritu Shah
Date: 15 September 2026
Time: 10:30 AM
Patient: Rahul Sharma

Would you like me to confirm this appointment?
```

The appointment should only be created after confirmation.

---

# 15. Appointment Booking

After confirmation:

```text
Confirm appointment
        ↓
Validate required information
        ↓
Check slot/appointment availability again
        ↓
Create appointment
        ↓
Return booking result
```

Availability should be checked again immediately before booking.

This protects against a slot becoming unavailable between initial selection and final confirmation.

---

# 16. Booking Race Conditions

Application-level availability checks are not enough for production.

Example:

```text
User A checks 10:30 AM
        ↓
Available

User B checks 10:30 AM
        ↓
Available

User A books

User B books
```

Both requests could theoretically pass an application-level check.

Production hardening should therefore use database-level protection or transactional booking logic.

This will be addressed during the database/security hardening phase.

---

# 17. Appointment State

The appointment workflow may maintain state similar to:

```text
appointment_data:
    doctor_id
    appointment_date
    appointment_time
    slot_id
    symptoms
    booking_confirmed
```

Not every field is required at every stage.

For example:

### Availability stage

```text
doctor_id
appointment_date
```

### Slot selection stage

```text
doctor_id
appointment_date
appointment_time
slot_id
```

### Confirmation stage

```text
doctor_id
appointment_date
appointment_time
slot_id
patient_id
symptoms
booking_confirmed
```

---

# 18. Waiting for User Input

A workflow can pause when information is required from the user.

Examples:

```text
awaiting_input = "phone"
```

```text
awaiting_input = "patient_selection"
```

```text
awaiting_input = "slot_selection"
```

```text
awaiting_input = "booking_confirmation"
```

The workflow status becomes:

```text
waiting_for_user
```

which is persisted in the database as:

```text
paused
```

---

# 19. Workflow Resumption

When the user sends the next message, the existing workflow state should be reused.

Example:

```text
Message 1:
"I want to book Dr. Ritu Shah."

        ↓

Workflow asks:
"Which slot would you like?"

        ↓

Workflow pauses

        ↓

User:
"10:30 AM"

        ↓

Existing workflow resumes
```

The system should not create a new unrelated workflow for the second message.

---

# 20. GraphState

The workflow uses a shared `GraphState`.

Current important fields include:

```text
user_input
session_id
messages

intent

patient_data
patient_lookup
selected_patient

request_data

selected_doctor
doctors_found

appointment_data

tool_result

workflow_id
current_agent
awaiting_input
next_step

workflow_status
last_error

response
```

The state is shared between graph nodes.

---

# 21. Workflow Lifecycle

The application-level workflow lifecycle is:

```text
started
   ↓
in_progress
   ↓
waiting_for_user
   ↓
in_progress
   ↓
completed
```

A workflow can also fail:

```text
in_progress
   ↓
failed
```

Database representation:

```text
started          → running
in_progress      → running
waiting_for_user → paused
completed        → completed
failed           → failed
```

---

# 22. LangGraph Routing

LangGraph controls which node executes next.

Conceptually:

```text
                    ┌──────────────┐
                    │  Supervisor  │
                    └──────┬───────┘
                           │
             ┌─────────────┼─────────────┐
             │             │             │
             ▼             ▼             ▼
        Reception       Doctor       Appointment
             │             │             │
             ▼             ▼             ▼
       Registration      END          Reception
```

The actual graph can evolve as workflows become more complex.

Routing logic should remain explicit rather than hiding major workflow decisions inside individual agents.

---

# 23. Entry Routing

When a message enters the system, the workflow first determines whether an existing workflow is waiting for a specific input.

Example:

```text
awaiting_input = "slot_selection"
```

The next user message should be routed to the Appointment workflow rather than being interpreted as an entirely new request.

Similarly:

```text
awaiting_input = "phone"
```

should route to the appropriate patient-identification workflow.

This prevents conversational follow-ups from being misclassified.

---

# 24. Contextual Follow-Ups

The workflow should preserve relevant context.

Example:

```text
User:
"What is Dr. Ritu Shah's fee?"

Assistant:
"Her consultation fee is ₹700."

User:
"Book her tomorrow."
```

The second request can use:

```text
selected_doctor
```

from workflow context.

The system should not require the user to repeat:

```text
Dr. Ritu Shah
```

unless the context is ambiguous.

---

# 25. Context Safety

Context should only be used when the reference can be resolved confidently.

Examples:

```text
"book this doctor"
```

may refer to:

```text
selected_doctor
```

If no doctor is selected, the system should ask for clarification.

The system must not invent a doctor.

Similarly:

```text
"book the second doctor"
```

can only be resolved if:

```text
doctors_found
```

contains a second doctor.

---

# 26. Error Handling

Errors should be represented explicitly.

Example:

```text
last_error
```

can contain the error message associated with a failed workflow.

A workflow failure should:

```text
1. Record the failure.
2. Persist the workflow status.
3. Avoid claiming that the action succeeded.
4. Provide an appropriate user-facing response.
```

The system must never tell the user that an appointment was booked unless the booking operation actually succeeded.

---

# 27. Workflow Completion

A workflow should be marked completed only when its intended business objective has actually been completed.

Examples:

### Doctor fee request

```text
Fee retrieved
    ↓
Response returned
    ↓
Completed
```

### Patient registration

```text
Patient created successfully
    ↓
Completed
```

### Appointment booking

```text
Appointment created successfully
    ↓
Completed
```

A workflow that is merely waiting for user input must not be marked completed.

---

# 28. Workflow Persistence

Important workflow state is persisted in:

```text
workflow_runs
```

The persisted information includes:

- workflow ID
- session ID
- current agent
- current node
- workflow state
- workflow status

Persistence allows workflows to survive beyond a single function call.

---

# 29. Streamlit Continuation

The Streamlit application maintains workflow state in:

```text
st.session_state.workflow_state
```

The general flow is:

```text
User message
    ↓
WorkflowRunner
    ↓
LangGraph
    ↓
Updated GraphState
    ↓
Streamlit session state
    ↓
Next user message
    ↓
WorkflowRunner
```

The workflow ID remains associated with the conversation.

---

# 30. WorkflowRunner Responsibilities

`WorkflowRunner` is responsible for:

- creating a workflow ID when required
- initializing state
- invoking the graph
- persisting workflow progress
- handling workflow completion
- handling waiting states
- handling failures

It should not contain business rules such as:

```text
Which doctor should be selected?
```

or:

```text
Whether a patient exists?
```

Those decisions belong to agents/services.

---

# 31. Tool Boundaries

Tools are thin wrappers.

Example:

```text
AppointmentAgent
      ↓
AppointmentTool
      ↓
AppointmentService
      ↓
AppointmentRepository
      ↓
Supabase
```

The tool should not contain complex business logic.

---

# 32. Service Boundaries

Services contain business rules.

For example:

```text
AppointmentService
```

can:

- validate appointment fields
- check whether an appointment already exists
- interpret repository results
- prepare booking data
- return structured success/failure results

The service should not decide conversational responses.

That remains the responsibility of the agent.

---

# 33. Repository Boundaries

Repositories contain database access only.

Example:

```text
AppointmentRepository
```

can execute:

```text
find_available_slots_by_doctor_and_date()
find_existing_appointment()
create_appointment()
```

It should not contain:

```text
"Please choose another slot."
```

or other conversational/business workflow decisions.

---

# 34. Example Complete Appointment Workflow

Example user conversation:

```text
User:
"What is Dr. Ritu Shah's consultation fee?"

        ↓

Supervisor
        ↓
Doctor Agent
        ↓
DoctorTool
        ↓
DoctorService
        ↓
DoctorRepository
        ↓
Supabase

Assistant:
"Dr. Ritu Shah's consultation fee is ₹700."

User:
"I want to book her tomorrow."

        ↓

Supervisor
        ↓
Appointment Agent
        ↓
Identify doctor + date
        ↓
AppointmentTool
        ↓
AppointmentService
        ↓
AppointmentRepository
        ↓
appointment_slots

Assistant:
"Available slots tomorrow:
1. 09:30 AM
2. 10:30 AM
3. 02:00 PM"

User:
"10:30 AM"

        ↓

Appointment Agent
        ↓
Store selected slot
        ↓
Patient identification

Assistant:
"May I have your mobile number?"

User:
"9876543210"

        ↓

Reception
        ↓
PatientTool
        ↓
PatientService
        ↓
PatientRepository
        ↓
Supabase

        ↓
Patient identified

Assistant:
"You're booking:

Dr. Ritu Shah
Tomorrow
10:30 AM
Rahul Sharma

Would you like me to confirm?"

User:
"Yes"

        ↓

Appointment Agent
        ↓
Verify slot availability
        ↓
Create appointment
        ↓
AppointmentService
        ↓
AppointmentRepository
        ↓
Supabase

Assistant:
"Your appointment has been booked successfully."
```

---

# 35. Important Workflow Separation

The following concepts must remain separate:

```text
Intent
    ≠
Availability
    ≠
Slot selection
    ≠
Patient identification
    ≠
Booking confirmation
    ≠
Appointment creation
```

Combining these stages creates ambiguous workflows and makes error handling difficult.

---

# 36. Current Development Priority

The next appointment implementation should follow:

```text
1. Identify doctor
2. Identify requested date
3. Retrieve available slots
4. Show slots
5. Wait for slot selection
6. Store selected slot
7. Identify patient
8. Handle existing/new/multiple patient
9. Ask for booking confirmation
10. Re-check availability
11. Create appointment
12. Return booking result
13. Persist workflow state
```

This sequence is the target architecture for the appointment workflow.

---

# 37. Future Workflow Extensions

The workflow architecture should eventually support:

- document upload
- follow-up workflows
- appointment cancellation
- appointment rescheduling
- reminders
- human escalation
- workflow recovery
- audit logging
- authentication and authorization

These should be added incrementally.

They should not be implemented by making the Supervisor responsible for everything.

---

# 38. Summary

MediFlow AI uses a stateful, multi-agent workflow architecture.

The key workflow pattern is:

```text
User
 ↓
Supervisor
 ↓
Specialized Agent
 ↓
Tool
 ↓
Service
 ↓
Repository
 ↓
Supabase
```

For appointment booking specifically:

```text
Availability
    ↓
Slot Selection
    ↓
Patient Identification
    ↓
Confirmation
    ↓
Booking
```

The workflow must preserve state between messages, pause when user input is required, and resume from the correct point.

The system must never claim that an action succeeded unless the underlying operation actually succeeded.
