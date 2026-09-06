# MediFlow AI — Architecture

## 1. Project Goal

MediFlow AI is a healthcare administration assistant designed to help patients with administrative workflows such as:

- Patient identification
- Patient registration
- Doctor discovery and recommendation
- Doctor information and consultation fees
- Doctor availability
- Appointment booking
- Document handling
- Follow-up workflows
- Safety and escalation workflows

The system should behave as a reliable healthcare administration assistant, not as a medical diagnosis system.

The priorities are:

1. Correctness
2. Patient safety
3. Privacy and security
4. Workflow reliability
5. Maintainability
6. Clear separation of responsibilities
7. Testability
8. Incremental development

## 2. High-Level Architecture

The core backend architecture is:

Agent
→ Tool
→ Service
→ Repository
→ Supabase

Each layer has a clearly defined responsibility.

### Agents

Agents are decision makers.

They determine what should happen next in a workflow and interact with tools to accomplish that goal.

Agents should not directly access the database.

Agents should not contain database queries.

Agents should not bypass the service layer.

### Tools

Tools are thin wrappers around services.

Their responsibility is to expose backend capabilities to agents.

Tools should contain minimal logic.

Typical flow:

Agent
→ Tool.method()
→ Service.method()

### Services

Services contain business logic.

They are responsible for:

- Validation
- Business rules
- Workflow-related decisions that belong to the backend
- Coordinating repository operations
- Returning structured results

Services should not be responsible for conversational decision making.

### Repositories

Repositories handle database access only.

They are responsible for:

- SELECT operations
- INSERT operations
- UPDATE operations
- DELETE operations
- Database-specific queries

Repositories should not contain conversational logic or agent decisions.

### Supabase

Supabase is the persistence layer.

Application code accesses Supabase through repositories rather than allowing agents or tools to directly query the database.

## 3. Agent Architecture

Agents live at the top level of the project.

Current agents include:

- Supervisor
- Reception
- Patient Identification
- Registration
- Doctor
- Appointment

### Supervisor

The Supervisor is the coordinator / decision maker.

Its responsibilities include:

- Understanding the user's request
- Classifying intent
- Extracting explicitly provided information
- Deciding which specialized workflow should handle the request
- Coordinating specialized agents through the workflow

The Supervisor should not directly perform database operations.

It should not claim that an action was completed unless the appropriate workflow actually completed it.

### Reception Agent

Reception handles patient-entry workflows.

Its responsibilities include:

- Requesting the patient's mobile number when required
- Looking up patients by phone
- Handling zero matching patients
- Handling one matching patient
- Handling multiple patients sharing a phone number
- Asking the user to select the correct patient when multiple matches exist

### Patient Identification

Patient identification is verification-based.

The system must not blindly trust statements such as:

"I am an existing patient."

The system should verify the patient against the database.

The expected flow is:

User provides mobile number
→ Search database
→ No patients
→ Registration

or:

User provides mobile number
→ One patient
→ Select patient

or:

User provides mobile number
→ Multiple patients
→ Show candidates
→ User selects patient
→ Select patient

Important design decision:

A mobile number is NOT assumed to uniquely identify a patient because family members may share the same mobile number.

### Registration Agent

Registration handles creation of a new patient record.

It collects required information such as:

- First name
- Age
- Mobile number

It validates required fields before creating the patient.

After successful registration, the newly created patient becomes the selected patient for the current workflow when appropriate.

### Doctor Agent

The Doctor Agent handles doctor-related workflows such as:

- Doctor recommendation
- Doctor search
- Doctor consultation fee
- Doctor availability
- Doctor selection

It should use doctor tools rather than accessing the database directly.

### Appointment Agent

The Appointment Agent handles appointment workflows including:

- Doctor selection
- Date selection
- Availability lookup
- Slot selection
- Patient identification when required
- Booking confirmation
- Appointment creation

Appointment workflow design is intentionally being refined to separate:

Availability
→ Slot Selection
→ Patient Identification
→ Confirmation
→ Booking

A user should be able to view available appointment slots before being asked for patient identification.

Patient identification is required when the workflow is actually proceeding toward booking.

## 4. Workflow Architecture

LangGraph is used for workflow orchestration.

The workflow graph connects the Supervisor and specialized agents.

Conceptually:

User
→ Workflow Runner
→ LangGraph
→ Supervisor / Specialized Agent
→ Tool
→ Service
→ Repository
→ Supabase

The graph is responsible for routing between workflow nodes.

The graph should not contain business logic that belongs in services.

Agents make decisions within their responsibilities.

The workflow maintains state between conversational turns.

## 5. Graph State

The workflow state contains information required to continue a conversation.

Important state categories include:

### Conversation

- user_input
- session_id
- messages

### Supervisor

- intent

### Patient

- patient_data
- patient_lookup
- selected_patient

### Request

- request_data

### Doctor

- selected_doctor
- doctors_found

### Appointment

- appointment_data

### Workflow

- workflow_id
- current_agent
- awaiting_input
- next_step
- workflow_status

### Error handling

- last_error

### Response

- response

The state should be treated as workflow state, not as a replacement for the database.

## 6. Workflow Lifecycle

Application-level workflow states are:

- started
- in_progress
- waiting_for_user
- completed
- failed

These map to the database workflow states:

| Application State | Database State |
| ----------------- | -------------- |
| started           | running        |
| in_progress       | running        |
| waiting_for_user  | paused         |
| completed         | completed      |
| failed            | failed         |

The workflow runner is responsible for starting and updating workflow lifecycle state.

A workflow that requires additional user input should remain active and be represented as waiting for user input rather than being incorrectly marked as completed.

## 7. Workflow Persistence

Workflow runs are persisted in the `workflow_runs` table.

The workflow record contains information such as:

- workflow ID
- session ID
- current agent
- current node
- workflow state
- status
- timestamps

Workflow persistence allows the application to track:

- Where a workflow currently is
- Whether it is waiting for the user
- Whether it completed
- Whether it failed
- Relevant workflow state required for continuation

## 8. Conversation and State Continuation

The Streamlit application maintains the current workflow state in session state.

The Workflow Runner receives:

- User input
- Session ID
- Existing workflow state when continuing a conversation

For a new workflow, a workflow ID is generated.

For an existing workflow, the existing workflow ID and state are reused.

The Runner invokes the LangGraph workflow and persists the resulting workflow state.

## 9. Security and Privacy Principles

MediFlow AI handles potentially sensitive healthcare information.

Therefore:

- Agents must not expose unnecessary patient information.
- Database access must remain behind repositories.
- Patient information should only be retrieved when required.
- Workflow persistence should avoid storing unnecessary sensitive information.
- Authentication and authorization must be considered before production use.
- Database Row Level Security and access controls must be reviewed before production deployment.
- Logs and audit records must not unnecessarily expose sensitive patient information.

Security and privacy hardening will be addressed as a dedicated development phase.

## 10. Important Architectural Rules

### Rule 1 — Layer separation

The architecture remains:

Agent
→ Tool
→ Service
→ Repository
→ Supabase

Do not bypass layers without a strong architectural reason.

### Rule 2 — Agents do not query databases

Agents interact with backend capabilities through tools.

### Rule 3 — Tools stay thin

Tools should not become business-logic containers.

### Rule 4 — Services contain business logic

Validation and business rules belong in services when they are backend/business concerns.

### Rule 5 — Repositories contain database access

Repositories should remain focused on persistence and database queries.

### Rule 6 — Supervisor coordinates

The Supervisor should coordinate and route work rather than directly performing specialized backend operations.

### Rule 7 — Verify patient identity

Never assume that the user's claim about being an existing/new patient is correct.

Verify through the patient database when patient identification is required.

### Rule 8 — Phone numbers are not unique patient identifiers

Multiple patients may share a mobile number.

The system must support selecting between multiple matching patients.

### Rule 9 — Do not identify patients unnecessarily

Patient identification should happen only when the workflow actually requires it.

For example, appointment availability should not require patient identification.

### Rule 10 — Preserve workflow state

Conversational workflows may span multiple user messages.

The state required to continue the workflow must be preserved between turns.

### Rule 11 — Do not mark incomplete workflows as completed

If the system is waiting for user input, the workflow should remain active/paused rather than being marked completed.

### Rule 12 — GitHub is the source of truth for code

GitHub contains the actual source code.

Project documentation describes architecture, decisions, requirements, and development plans.

The Project is not a replacement for version control.

## 11. Development Workflow

Development follows this process:

Discuss / Design
→ Implement
→ Test locally
→ Verify
→ Commit
→ Push to GitHub
→ Continue to next phase

Changes should be incremental.

Avoid modifying many unrelated parts of the system in one change.

Before major architectural changes, inspect the current GitHub code to ensure that the implementation being changed is understood correctly.

## 12. Architectural Decision Philosophy

MediFlow AI should favor simple, maintainable architecture over unnecessary complexity.

New components should only be introduced when they solve a real problem.

When an architectural change is proposed, evaluate:

1. What problem does it solve?
2. Is the problem actually present?
3. Is there a simpler solution?
4. What are the trade-offs?
5. Does it preserve separation of responsibilities?
6. Does it improve reliability and maintainability?
7. Does it introduce unnecessary complexity or security risk?

Previously agreed architectural decisions should not be changed casually.

Changes should be made when there is a clear technical reason.

## 13. Current Architectural Direction

The project is currently moving from a working prototype toward a more reliable production-oriented architecture.

The next major improvement is the appointment workflow:

Availability
→ Slot Selection
→ Patient Identification
→ Confirmation
→ Booking

This will be implemented incrementally and tested before moving to subsequent features.
