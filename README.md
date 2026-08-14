# ICCTECH IT Service Management

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

## 4. Analysis and design

### Architecture

ICCTECH uses a containerised deployment architecture hosted on a Linode Linux cloud server. Users access the system through a web browser, while Docker separates the PHP web application from the MySQL database and uses persistent volumes to retain operational data and protected application files.

```text
End user / Support analyst / Administrator
                    |
                    v
             Web browser
                    |
              HTTP port 8080
                    |
                    v
        Linode Linux cloud server
                    |
                    v
       Docker application container
          Apache + PHP 8.4
                    |
          PHP application modules
       Authentication and role access
                    |
                PDO/MySQL
                    |
                    v
         Docker MySQL 8.0 container
                    |
                    v
       Persistent database volume

Additional persistent volumes:
- Ticket attachments
- Change-management attachments
- Application encryption keys
```

The application container exposes Apache on port 80, which Docker maps to port 8080 on the Linode host. The application communicates with the separate MySQL container over the internal Docker network. Persistent Docker volumes protect the database, uploaded attachments and encryption keys from being lost when containers are recreated.

### Core ticket workflow

```text
Ticket submitted
       |
       v
Open: triaged, categorised, prioritised and assigned
       |
       v
In Progress
   |         \
   v          v
On Hold    Awaiting Response
   |          |
   +----------+
       |
       v
In Progress
       |
       v
Closed

A closed ticket may be reopened if further work is required.
```

`Open`, `In Progress`, `On Hold`, `Awaiting Response` and `Closed` are the default ticket statuses. Triage, categorisation, prioritisation, assignment and analyst communication are ticket-handling activities rather than separate statuses. Statuses are configurable by an administrator, and `On Hold` and `Awaiting Response` pause the service-level agreement clock by default.

The detailed SRS, use cases, data model, UI evidence and selected design diagrams should be included in the submitted `Project_Documentation.pdf` or linked supporting documentation.

## 5. Technology and local setup

### Technology stack

- PHP 8.4 with Apache HTTP Server
- MySQL 8.0
- PDO with the `pdo_mysql` database driver
- Required PHP extensions: cURL, OpenSSL and Mbstring
- Optional PHP extension: IMAP for IMAP mailbox collection
- HTML, CSS, vanilla JavaScript and TinyMCE
- Docker and Docker Compose for containerised deployment
- Docker volumes for database data, attachments and encryption keys

### Prerequisites

Install Git, Docker Engine and Docker Compose. Ensure ports `8080` and `3307` are available on the local computer.

### Docker-based local setup

```bash
git clone https://github.com/Clemzy123/ICCTECH.git
cd ICCTECH
docker compose up --build -d
```

Docker Compose builds the Apache/PHP application container, starts MySQL 8.0 and imports the initial schema from `database/freeitsm.sql`. The first application-container startup also generates an encryption key in its persistent Docker volume.

### Verify the installation

Run `docker compose ps` to confirm that the application and database containers are running. Open [http://localhost:8080/setup/](http://localhost:8080/setup/) to check the PHP environment, database connection, encryption key and database schema. The setup page verifies the installation; the database schema is imported automatically when the MySQL data volume is first created.

After the checks pass, open [http://localhost:8080/](http://localhost:8080/) to use the application. Use `docker compose logs` when troubleshooting container startup or database-connection problems.

### Local configuration and security

The credentials in `docker-compose.yml` and the initial administrator account are development defaults intended only for local evaluation. Replace all default database and administrator passwords before any public or production deployment. Supply production secrets through protected environment configuration, restrict database exposure and never commit passwords, encryption keys or other credentials to the repository.

## 6. Testing and quality assurance

Testing evidence must record the date, environment, expected result, actual result, pass/fail outcome, defects and corrective action. Complete this table with executed results before submission.

| Test ID | Scenario                       | Expected result                                             | Actual result       | Status          |
| ------- | ------------------------------ | ----------------------------------------------------------- | ------------------- | --------------- |
| TC-01   | Analyst authentication         | Valid analyst reaches authorised workspace.                 | **[Record result]** | **[Pass/Fail]** |
| TC-02   | End user submits a ticket      | Ticket is stored and receives a reference/status.           | **[Record result]** | **[Pass/Fail]** |
| TC-03   | Analyst updates/assigns ticket | Changes persist and are visible to authorised users.        | **[Record result]** | **[Pass/Fail]** |
| TC-04   | Role access check              | Restricted functions are unavailable to unauthorised users. | **[Record result]** | **[Pass/Fail]** |
| TC-05   | Knowledge search               | Relevant visible article can be found and opened.           | **[Record result]** | **[Pass/Fail]** |
| TC-06   | Production smoke test          | Deployed URL loads and core ticket workflow works.          | **[Record result]** | **[Pass/Fail]** |

## 7. Technical debt register

| Debt                                     | Cause                                                 | Impact                                                  | Priority | Proposed resolution                                                                |
| ---------------------------------------- | ----------------------------------------------------- | ------------------------------------------------------- | -------- | ---------------------------------------------------------------------------------- |
| Unconfigured external integrations       | 48-hour scope and unavailable provider credentials.   | Some communication channels are not demonstrated.       | Medium   | Configure and test integrations in a later release using secured service accounts. |
| Limited project-specific automated tests | Timeboxed adaptation work.                            | Regression confidence is reduced for local changes.     | High     | Add a repeatable automated test suite for every project-specific change.           |
| Documentation placeholders               | Personal/deployment details are pending verification. | Submission evidence is incomplete if left unresolved.   | Critical | Replace all bracketed placeholders and validate links before Sakai submission.     |
| Broad upstream feature set               | The base platform exceeds examination scope.          | Reviewers may not distinguish reused and original work. | High     | Maintain a change log and clearly document every student-authored adaptation.      |

## 8. Deployment and access details

ICCTECH is deployed on a Linode cloud server using a Linux-based environment, PHP, MySQL and a web server. The deployed system is remotely accessible at [http://45.79.223.146:8080/index.php](http://45.79.223.146:8080/index.php).

| Item             | Value                                                                      |
| ---------------- | -------------------------------------------------------------------------- |
| Live application | [http://45.79.223.146:8080/index.php](http://45.79.223.146:8080/index.php) |
| Admin URL        | [http://45.79.223.146:8080/index.php](http://45.79.223.146:8080/index.php) |
| Test username    | `admin`                                                                    |
| Test password    | `freeitsm`                                                                 |
| Admin username   | `admin`                                                                    |
| Admin password   | `freeitsm`                                                                 |

Before submitting, verify the deployed application, database connectivity, role access and examiner credentials. Keep the deployment accessible for grading. Change these default credentials after grading or before any public/long-term deployment.

## 9. Maintenance, future evolution and limitations

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
