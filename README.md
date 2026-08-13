# ICCTECH: IT Service Management Solution

> **University of Ghana — CSCD602 Advanced Software Engineering**<br>
> Individual Project-Based Examination, First Semester 2025/2026

| Item                              | Details                                                              |
| --------------------------------- | -------------------------------------------------------------------- |
| Student developer / project owner | [Clemzy123](https://github.com/Clemzy123)                            |
| Student name                      | **Clement Asamoah**                                                  |
| Student ID                        | **22424193**                                                         |
| Project status                    | Functional adaptation and deployment project                         |
| Live application                  | **http://45.79.223.146:8080/index.php**                              |
| Source repository                 | [github.com/Clemzy123/ICCTECH](https://github.com/Clemzy123/ICCTECH) |

## 1. Project overview

ICCTECH is a self-hosted IT Service Management (ITSM) solution for organisations that need a central place to log, assign, track and resolve IT support requests.

### Problem statement

IT support work is often managed through informal messages, email threads and spreadsheets. This makes request ownership, status visibility, communication history and service reporting difficult to manage. ICCTECH provides a web-based workspace that centralises support tickets, users, assets, knowledge and related operational records.

### Aim

To deliver and document a deployable ITSM solution that improves the recording, assignment, tracking and resolution of IT support requests while demonstrating disciplined advanced software-engineering practice.

### Objectives

- Analyse the support-management problem and define prioritised requirements.
- Design and implement the core architecture and workflows required for the ICCTECH IT Service Management system.
- Demonstrate core ticket, user-access, knowledge and asset-management workflows.
- Test the implemented scope and document defects, limitations and technical debt.
- Produce a maintainable deployment and an evolution plan.

### Stakeholders and intended users

| Stakeholder                | Interest / role                                                                |
| -------------------------- | ------------------------------------------------------------------------------ |
| Support analysts           | Receive, assign, update and resolve service requests.                          |
| End users                  | Submit requests, view progress and access self-service information.            |
| IT manager / administrator | Configure users, permissions, service processes and reports.                   |
| Organisation management    | Monitor service quality and operational trends.                                |
| Student developer          | Owns the documented adaptation, configuration, validation and deployment work. |

## 2. Scope and features

- Authentication and role-based access for analysts and end users.
- Ticket logging, categorisation, assignment, communication, status tracking and resolution.
- End-user self-service portal and knowledge-base access.
- Asset records associated with support operations.
- Administrative configuration, basic audit/reporting views and database-backed persistence.
- Responsive web access through a PHP and MySQL deployment.

## 3. Requirements and SRS summary

### Functional requirements

| ID    | Requirement                                                                     | Priority |
| ----- | ------------------------------------------------------------------------------- | -------- |
| FR-01 | Users shall be able to authenticate according to their assigned role.           | Must     |
| FR-02 | End users shall be able to create and view support tickets.                     | Must     |
| FR-03 | Analysts shall be able to assign, update, communicate on and resolve tickets.   | Must     |
| FR-04 | Administrators shall be able to manage users, permissions and service settings. | Must     |
| FR-05 | Users shall be able to search and read relevant knowledge articles.             | Should   |
| FR-06 | Analysts shall be able to record and view asset information.                    | Should   |
| FR-07 | Administrators shall be able to view operational/audit information.             | Could    |

### Non-functional requirements

- **Usability:** Core service-desk functions such as creating, assigning, updating and resolving tickets shall be easy to understand and use without requiring specialist technical training.
- **Security:** The system shall require authenticated access and enforce role-based permissions for administrators, analysts and end users. User input shall be validated, and sensitive configuration information shall be handled securely.
- **Reliability:** Application data shall be persistently stored in the MySQL database so that tickets, users, assets and other operational records remain available between sessions. System errors shall provide meaningful information to support troubleshooting.
- **Compatibility:** The solution shall operate within a Linux-based web-server environment supporting PHP 7.4–8.4 and MySQL 8.0 or later and shall be accessible through commonly used web browsers.
- **Deployability:** The application shall be capable of being deployed to a cloud-hosted web server for remote access. The final ICCTECH solution is deployed on a Linode cloud server and is accessible through the verified live application URL: http://45.79.223.146:8080/index.php.

### Prioritisation method

MoSCoW prioritisation was used. “Must” requirements define the minimum viable, demonstrable service-desk workflow; “Should” requirements improve operational usefulness; “Could” requirements are deferred when time is constrained.

## 4. Effort estimation and lifecycle

### Estimation approach

The project uses expert estimation with timeboxing because the examination has a fixed 48-hour duration and the work is a scoped adaptation/deployment rather than greenfield development. Estimates guide what evidence and configuration can be completed without compromising the required core workflow.

| Activity                                        | Estimated hours |
| ----------------------------------------------- | --------------: |
| Requirements, scope and estimation              |               6 |
| Analysis and design artefacts                   |               6 |
| Environment setup, configuration and adaptation |              17 |
| Testing and defect correction                   |               7 |
| Deployment and production verification          |               4 |
| Documentation and submission checks             |               8 |
| **Total**                                       |          **48** |

**Assumptions:** a suitable PHP/MySQL or Docker environment is available; the upstream codebase is available under its licence; and external service credentials are not required for the minimum scope.<br>
**Constraint:** the 48-hour examination limit requires strict prioritisation and documented deferral of non-core work.

## 5. Analysis and design

### Architecture

```text
End user / Support analyst
           |
           v
Browser interface (self-service portal / analyst workspace)
           |
           v
PHP application modules and authentication/authorisation layer
           |
           v
MySQL database (tickets, users, assets, knowledge and audit data)
```

### Core ticket workflow

```text
Ticket submitted -> Categorised -> Assigned -> In progress
                                      |             |
                                      v             v
                                  Updated <--- Analyst response
                                                    |
                                                    v
                                             Resolved / Closed
```

The detailed SRS, use cases, data model, UI evidence and selected design diagrams should be included in the submitted `Project_Documentation.pdf` or linked supporting documentation.

## 6. Technology and local setup

- PHP 7.4–8.4
- MySQL 8.0+
- Apache or another PHP-capable web server
- Vanilla JavaScript and TinyMCE
- Docker Compose (recommended for local evaluation)

```bash
git clone https://github.com/Clemzy123/ICCTECH.git
cd ICCTECH
docker compose up -d
```

Open `http://localhost:8080/setup/` to complete local installation. Configure the database and application secrets before using the system. Do not publish default or real credentials in a public repository.

## 7. Testing and quality assurance

Testing evidence must record the date, environment, expected result, actual result, pass/fail outcome, defects and corrective action. Complete this table with executed results before submission.

| Test ID | Scenario                       | Expected result                                             | Actual result       | Status          |
| ------- | ------------------------------ | ----------------------------------------------------------- | ------------------- | --------------- |
| TC-01   | Analyst authentication         | Valid analyst reaches authorised workspace.                 | **[Record result]** | **[Pass/Fail]** |
| TC-02   | End user submits a ticket      | Ticket is stored and receives a reference/status.           | **[Record result]** | **[Pass/Fail]** |
| TC-03   | Analyst updates/assigns ticket | Changes persist and are visible to authorised users.        | **[Record result]** | **[Pass/Fail]** |
| TC-04   | Role access check              | Restricted functions are unavailable to unauthorised users. | **[Record result]** | **[Pass/Fail]** |
| TC-05   | Knowledge search               | Relevant visible article can be found and opened.           | **[Record result]** | **[Pass/Fail]** |
| TC-06   | Production smoke test          | Deployed URL loads and core ticket workflow works.          | **[Record result]** | **[Pass/Fail]** |

## 8. Technical debt register

| Debt                                     | Cause                                                 | Impact                                                  | Priority | Proposed resolution                                                                |
| ---------------------------------------- | ----------------------------------------------------- | ------------------------------------------------------- | -------- | ---------------------------------------------------------------------------------- |
| Unconfigured external integrations       | 48-hour scope and unavailable provider credentials.   | Some communication channels are not demonstrated.       | Medium   | Configure and test integrations in a later release using secured service accounts. |
| Limited project-specific automated tests | Timeboxed adaptation work.                            | Regression confidence is reduced for local changes.     | High     | Add a repeatable automated test suite for every project-specific change.           |
| Documentation placeholders               | Personal/deployment details are pending verification. | Submission evidence is incomplete if left unresolved.   | Critical | Replace all bracketed placeholders and validate links before Sakai submission.     |
| Broad upstream feature set               | The base platform exceeds examination scope.          | Reviewers may not distinguish reused and original work. | High     | Maintain a change log and clearly document every student-authored adaptation.      |

## 9. Deployment and access details

| Item             | Value                              |
| ---------------- | ---------------------------------- |
| Live application | **[Add URL]**                      |
| Admin URL        | **[Add URL]**                      |
| Test username    | **[Provide securely to examiner]** |
| Test password    | **[Provide securely to examiner]** |
| Admin username   | **[Provide securely to examiner]** |
| Admin password   | **[Provide securely to examiner]** |

Before submitting, verify the deployed application, database connectivity, role access and examiner credentials. Keep the deployment accessible for grading.

## 10. Maintenance, future evolution and limitations

### Maintenance strategy

- **Corrective:** log, prioritise and fix defects found through user feedback and testing.
- **Adaptive:** update deployment settings and integrations when hosting, organisational or API requirements change.
- **Perfective:** refine ticket categories, dashboards, knowledge content and user experience using operational feedback.
- **Preventive:** apply security updates, review dependencies, back up the database and regularly test restoration.

### Future evolution

- Add and test organisation-specific integrations after credentials and governance are available.
- Expand automated regression and security testing for project-specific changes.
- Introduce monitoring, backup verification and production performance baselines.
- Collect end-user feedback and prioritise improvements through the technical-debt register.

### Limitations

This submission is intentionally restricted to the documented core workflow and timeboxed adaptation work. Features inherited from the upstream codebase are not evidence of individual development unless separately documented with commit history, design rationale and testing evidence.
