# MediFlow AI — Development Roadmap

## 1. Purpose

This document defines the implementation roadmap for MediFlow AI.

The goal is to build a reliable healthcare administration assistant with:

- Stateful conversational workflows
- Patient registration and identification
- Doctor discovery and routing
- Appointment availability
- Appointment booking
- Document handling
- Follow-up workflows
- Human escalation
- Auditability
- Security and privacy
- Testing
- Production-oriented architecture

Development will happen incrementally.

Each phase should be completed, tested, verified, committed, and pushed to GitHub before moving to the next major phase.

---

# 2. Development Principles

The project follows this development cycle:

```text
Discuss / Design
       ↓
Implement
       ↓
Test locally
       ↓
Verify behavior
       ↓
Commit
       ↓
Push to GitHub
       ↓
Next phase
```

Important rules:

- Do not make unrelated changes together.
- Do not assume local code and GitHub are identical.
- Inspect GitHub when the current remote implementation matters.
- Preserve established architecture decisions.
- Prefer simple solutions over unnecessary abstraction.
- Do not introduce infrastructure before the feature requires it.
- Test important workflows rather than only individual functions.
- Never claim an operation succeeded unless the underlying operation succeeded.

---

# 3. Current Architecture

The core architecture is:

```text
Agent
  ↓
Tool
  ↓
Service
  ↓
Repository
  ↓
Supabase
```

Responsibilities:

### Agent

Decision making and conversation.

### Tool

Thin interface to backend capabilities.

### Service

Business logic and validation.

### Repository

Database access.

### Supabase

Persistent data storage.

---

# 4. Current Project Status

The following foundations have already been implemented:

- Supervisor agent
- Reception agent
- Patient identification
- Multiple patients sharing a phone number
- Patient registration
- Doctor search
- Doctor recommendation
- Doctor fee lookup
- Doctor availability
- Appointment availability foundation
- Appointment persistence foundation
- Supabase integration
- LangGraph orchestration
- Streamlit chat interface
- Conversational workflow continuation
- Workflow persistence
- Git repository
- GitHub repository
- Project architecture documentation
- Database documentation
- Workflow design documentation

The system is therefore beyond the initial prototype stage.

The next work should focus on making the existing workflows correct and reliable before adding many new features.

---

# 5. Phase 1 — Appointment Workflow Redesign

## Priority

Highest.

## Goal

Implement the correct appointment lifecycle:

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

## Tasks

1. Identify doctor.
2. Identify requested date.
3. Retrieve actual available slots.
4. Display available slots.
5. Wait for user slot selection.
6. Store selected slot.
7. Identify patient.
8. Handle:
   - existing patient
   - new patient
   - multiple patients
9. Ask for booking confirmation.
10. Re-check availability.
11. Create appointment.
12. Return booking result.
13. Persist workflow state.

## Important Rule

The user must not be required to provide a mobile number simply to view appointment availability.

---

# 6. Phase 2 — Appointment Data and Concurrency Hardening

After the workflow semantics are correct, harden appointment persistence.

## Tasks

- Review appointment constraints.
- Review appointment slot lifecycle.
- Prevent duplicate bookings.
- Add appropriate database constraints.
- Add indexes based on real queries.
- Re-check availability immediately before booking.
- Handle booking failures cleanly.
- Handle stale slots.
- Seed realistic future appointment slots.

## Goal

Make appointment booking reliable even when multiple booking attempts occur close together.

---

# 7. Phase 3 — Workflow State Hardening

The current workflow persistence foundation should be reviewed.

## Tasks

- Verify `workflow_runs` persistence.
- Verify pause/resume behavior.
- Verify workflow continuation across messages.
- Verify correct `current_node`.
- Separate graph node identity from `current_agent` if required.
- Ensure workflow completion is not marked prematurely.
- Ensure failed workflows are persisted correctly.
- Review what information is stored inside `workflow_state`.

## Important Issue

A workflow with no `awaiting_input` should not automatically be considered completed unless its intended business objective has actually finished.

---

# 8. Phase 4 — Audit Logging

Implement structured audit logging for important business actions.

## Events to consider

Examples:

```text
patient_lookup
patient_created
doctor_lookup
availability_checked
slot_selected
appointment_confirmation
appointment_created
document_uploaded
escalation_created
```

Each event should include only the information necessary for auditing.

Avoid storing unnecessary PHI in audit metadata.

## Goal

Provide a reliable history of important system actions without creating an unnecessary sensitive-data store.

---

# 9. Phase 5 — Document Upload

Implement the document workflow.

## Target flow

```text
User wants to upload document
        ↓
Identify patient
        ↓
Receive document
        ↓
Validate document
        ↓
Secure storage
        ↓
Store metadata
        ↓
Audit event
        ↓
Confirmation
```

## Database

Use:

```text
documents
```

for document metadata.

The actual file should be stored in secure object storage.

## Important

Document upload should not be implemented as an unrelated capability inside the Supervisor.

A dedicated workflow/agent should own the process.

---

# 10. Phase 6 — Follow-Up Workflow

Implement follow-up support.

Examples:

```text
"I want a follow-up for my previous appointment."

"Can I book a follow-up with the same doctor?"
```

## Target flow

```text
Identify patient
        ↓
Find relevant previous appointment
        ↓
Identify doctor / context
        ↓
Determine follow-up requirement
        ↓
Availability
        ↓
Slot selection
        ↓
Confirmation
        ↓
Booking
```

The follow-up workflow should reuse existing appointment capabilities where possible instead of duplicating booking logic.

---

# 11. Phase 7 — Human Escalation

Implement escalation for cases that should not be handled automatically.

Examples:

- unsupported administrative request
- unresolved workflow
- manual review required
- operational failure
- safety-sensitive situation requiring human handling

## Target flow

```text
Issue detected
    ↓
Create escalation
    ↓
Persist reason
    ↓
Assign / queue
    ↓
Human resolution
    ↓
Mark resolved
```

Use:

```text
escalations
```

for persistence.

The system should clearly communicate to the user when human intervention is required.

---

# 12. Phase 8 — Safety and Scope Controls

MediFlow AI is a healthcare administration assistant.

It should not behave as an unrestricted medical diagnosis system.

## Scope

The system can assist with administrative workflows such as:

- registration
- doctor discovery
- fees
- availability
- appointments
- documents
- follow-ups
- administrative escalation

## Safety behavior

When a request is outside the intended scope or requires human attention, the system should:

```text
Recognize limitation
        ↓
Avoid inventing medical advice
        ↓
Provide safe administrative guidance
        ↓
Escalate when appropriate
```

Safety logic should be explicit and testable.

---

# 13. Phase 9 — Security and Privacy Hardening

This is a major production-readiness phase.

## Tasks

### Secrets

- Remove secrets from source code.
- Use environment variables.
- Verify `.gitignore`.
- Never commit service-role keys.

### Database

- Review Row Level Security.
- Review authorization.
- Restrict patient data access.
- Restrict document access.
- Restrict workflow access.

### PHI

Review:

- application logs
- workflow state
- audit metadata
- error messages
- Streamlit state

Remove unnecessary patient information wherever possible.

### Input validation

Validate:

- phone numbers
- age
- IDs
- dates
- times
- appointment selections
- uploaded documents

---

# 14. Phase 10 — Testing

Testing should happen throughout development, not only at the end.

## Unit Tests

Test:

- input parsers
- services
- repository behavior where practical
- routing logic
- workflow state transitions

## Workflow Tests

Test complete conversations.

### Patient registration

```text
User
→ no patient
→ registration
→ patient created
```

### Existing patient

```text
User
→ phone
→ one patient
→ continue
```

### Shared phone

```text
User
→ phone
→ multiple patients
→ selection
→ continue
```

### Appointment

```text
doctor
→ date
→ slots
→ slot selection
→ patient
→ confirmation
→ booking
```

### Invalid input

Test:

- invalid phone
- invalid age
- invalid slot
- invalid patient selection
- unavailable appointment
- unknown doctor

### Failure cases

Test:

- database failure
- booking conflict
- missing workflow state
- malformed LLM response
- unexpected agent output

---

# 15. Phase 11 — Observability

The system should eventually provide useful operational visibility.

Track:

- workflow ID
- workflow status
- current workflow node
- agent execution
- tool execution
- service failures
- database failures
- appointment booking failures
- latency
- escalation count

Avoid logging sensitive patient information unnecessarily.

Observability should help answer:

```text
What happened?
Where did it fail?
Which workflow was affected?
Which component failed?
```

---

# 16. Phase 12 — API Layer

The current Streamlit application is useful for development and demonstration.

A future API layer can expose the workflow to other clients.

Potential architecture:

```text
Web / Mobile / Streamlit
          ↓
        API
          ↓
   WorkflowRunner
          ↓
      LangGraph
```

The API should not bypass the established service/repository architecture.

The Streamlit interface and API should eventually use the same workflow backend.

---

# 17. Phase 13 — Authentication and Authorization

Authentication should be introduced before production use.

Potential requirements:

- user authentication
- role-based access
- administrative permissions
- staff permissions
- patient data authorization
- document authorization
- escalation permissions

Authorization should be enforced at the appropriate backend/database boundaries.

The UI must not be treated as a security boundary.

---

# 18. Phase 14 — Production Database Hardening

Review the complete Supabase schema.

## Tasks

- migration management
- indexes
- foreign keys
- unique constraints
- check constraints
- RLS policies
- transaction handling
- concurrency protection
- backup/recovery
- retention policies

Database changes should be version-controlled.

---

# 19. Phase 15 — Deployment

After application and database hardening:

```text
Local
  ↓
Test environment
  ↓
Verification
  ↓
Production
```

Deployment should include:

- environment configuration
- database configuration
- secret management
- logging
- health checks
- error handling
- monitoring
- rollback strategy

---

# 20. Recommended Implementation Order

The project should not attempt all roadmap items simultaneously.

Recommended order:

```text
1. Appointment workflow redesign
        ↓
2. Appointment data/concurrency hardening
        ↓
3. Workflow state hardening
        ↓
4. Audit logging
        ↓
5. Document upload
        ↓
6. Follow-up workflow
        ↓
7. Human escalation
        ↓
8. Safety/scope controls
        ↓
9. Security/privacy hardening
        ↓
10. Comprehensive testing
        ↓
11. Observability
        ↓
12. API layer
        ↓
13. Authentication/authorization
        ↓
14. Production database hardening
        ↓
15. Deployment
```

This order prioritizes correctness of the core workflows before production infrastructure.

---

# 21. Definition of Done

A feature is not considered complete merely because the code runs.

A feature should satisfy:

```text
Implementation
    ↓
Unit tests
    ↓
Workflow test
    ↓
Error-path test
    ↓
Database verification
    ↓
User-facing behavior verification
    ↓
Git commit
    ↓
GitHub push
```

For important features, verify the actual persisted database state.

---

# 22. Git Workflow

GitHub is the source of truth for application code.

After completing a working phase:

```text
git status
        ↓
Review changes
        ↓
Run tests
        ↓
Commit
        ↓
Push
        ↓
Verify GitHub
```

Commit messages should describe the completed change.

Examples:

```text
Implement appointment slot selection flow
```

```text
Add workflow state persistence
```

```text
Add appointment booking tests
```

Avoid large commits containing unrelated changes.

---

# 23. Architecture Protection

The following architectural boundary should remain stable:

```text
Agent
  ↓
Tool
  ↓
Service
  ↓
Repository
  ↓
Supabase
```

Do not move database logic into agents simply because it is faster.

Do not move business rules into repositories.

Do not make tools responsible for workflow decisions.

Do not make the Supervisor responsible for every business operation.

If a future architectural change becomes necessary, document the reason before implementing it.

---

# 24. Incremental Development Strategy

Each major feature should be developed in a small loop.

Example:

```text
Design appointment step
        ↓
Change graph
        ↓
Change appointment agent
        ↓
Change supporting backend only if required
        ↓
Run focused tests
        ↓
Run complete workflow
        ↓
Verify Supabase
        ↓
Commit
        ↓
Push GitHub
```

Avoid changing:

```text
appointment
+
documents
+
escalations
+
authentication
+
database schema
```

in one uncontrolled change.

---

# 25. Current Immediate Task

The immediate implementation task is:

```text
Redesign appointment workflow
```

Target:

```text
User asks to book
        ↓
Doctor/date identified
        ↓
Available slots shown
        ↓
User selects slot
        ↓
Patient identified
        ↓
Booking confirmed
        ↓
Appointment created
```

Only after this workflow is working correctly should the project move to the next roadmap phase.

---

# 26. Final Project Goal

The final MediFlow AI system should provide a reliable administrative assistant capable of:

```text
Understand user request
        ↓
Determine workflow
        ↓
Collect required information
        ↓
Verify information
        ↓
Execute appropriate backend operation
        ↓
Persist workflow state
        ↓
Audit important actions
        ↓
Handle failures safely
        ↓
Escalate when required
        ↓
Give accurate user-facing response
```

The objective is not to build the largest possible system.

The objective is to build a system that is:

- correct
- maintainable
- secure
- testable
- explainable
- reliable
- extensible
- appropriate for healthcare administration

---

# 27. Project Documentation Set

The core project documentation is:

```text
01_ARCHITECTURE.md
02_DATABASE.md
03_WORKFLOW_DESIGN.md
04_ROADMAP.md
```

Together these documents define:

```text
Architecture
    +
Database
    +
Workflow behavior
    +
Development plan
```

They should be treated as living project documentation and updated when important architectural decisions change.
