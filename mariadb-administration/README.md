# Enterprise MariaDB Administration & High-Availability Infrastructure Engineering

This directory contains production-grade core database blueprints, automated hot-backup scripts, and replication engine frameworks designed to support mission-critical, high-concurrency MariaDB environments. These artifacts represent technical execution patterns optimized for large-scale enterprise infrastructures requiring 24/7 uptime and sub-second transactional response times.

---

## 📋 Project 1: Crash-Safe GTID Replication Engine Provisioning

### 🔹 Project Description
The infrastructure required a resilient, high-availability data layer to support a high-volume financial transaction platform. The existing environment suffered from frequent replication lag and broken master-slave synchronization links caused by unexpected hardware reboots and non-deterministic text-based log coordinate parsing.

### 🔹 My Role: Lead Database Infrastructure Architect
*   Designed and deployed a highly reliable Master-Slave replication topology utilizing native MariaDB Global Transaction ID (GTID) state machines.
*   Enforced strict `ROW`-based binary logging to guarantee absolute data consistency across cross-region nodes.
*   Hardened the slave nodes by transitioning metadata repositories from legacy flat files to transactionally secure InnoDB system tables (`master-info-repository = TABLE`), eliminating data drift risks.

---

## 📋 Project 2: Automated Non-Blocking Physical Enterprise Backup Solution

### 🔹 Project Description
The organization lacked a verified, crash-consistent hot backup workflow for a multi-terabyte MariaDB deployment. Legacy logical dumps (`mysqldump`) were causing massive table-locking bottlenecks during production hours, driving CPU utilization to 95% and causing transactional timeouts for end-users.

### 🔹 My Role: Senior Database Administrator & Automation Engineer
*   Engineered a fully automated, low-overhead shell script engine utilizing `mariabackup` to capture live physical system snapshots without locking active tables.
*   Implemented a multi-threaded `--prepare` stage directly inside the staging storage mount to apply uncommitted transaction logs, ensuring a verified point-in-time recovery (PITR) footprint.
*   Structured a secure logging matrix to track backup success and fail signals, matching compliance standards for corporate disaster recovery.

---

## 📋 Project 3: Production Diagnostics & Internal Resource Optimization

### 🔹 Project Description
An enterprise system was experiencing intermittent slowdowns and query queuing during peak business windows. The development team was unable to track down short-lived metadata deadlocks and memory page allocation issues that were driving down the InnoDB buffer pool efficiency.

### 🔹 My Role: Performance Tuning & Optimization Consultant
*   Authored advanced administrative diagnostic queries targeting active long-running threads to isolate and remove blocking application metadata locks.
*   Analyzed engine cache metrics to determine the exact InnoDB Buffer Pool cache hit ratio.
*   Optimized `my.cnf` memory layouts by dynamically sizing `innodb_buffer_pool_size` to 80% of system RAM and scaling buffer pool instances to eliminate internal mutex thread contention.
