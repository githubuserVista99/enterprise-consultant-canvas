# Playbook 2: Schema Migration (Oracle 19c On-Premise to AWS Aurora/RDS PostgreSQL)

This production playbook outlines the operational steps and conversion architecture required to safely migrate an enterprise Oracle 19c on-premise schema to an AWS PostgreSQL instance. PostgreSQL matches Oracle's enterprise features more closely, making it ideal for high-complexity PL/SQL blocks.

## 📊 Source Environment Topology
*   **Database Engine:** Oracle Database 19c Enterprise Edition
*   **Schema Footprint:** 1 Target Schema
*   **Storage Profiles:** 1 Dedicated Tablespace (`DATA_TS01`)
*   **Access Control Layer:** 3 Database Users (`app_admin`, `app_read`, `app_write`)
*   **Data Layer Objects:** 2 Core Transactional Tables (`customer_master`, `order_ledger`)
*   **Business Logic Units:** 1 PL/SQL Stored Procedure, 1 Custom Function

---

## 🛠️ Phase 1: Structural Schema & Target Data Type Mapping

PostgreSQL has native data types that match Oracle's architecture very closely, minimizing structural risks during ETL stages:

| Oracle 19c Data Type | AWS RDS PostgreSQL Target Type | Migration Strategy / Handling Note |
| :--- | :--- | :--- |
| `NUMBER(10,0)` | `INT` or `BIGINT` | Clean mapping for identity fields. |
| `NUMBER(18,2)` | `NUMERIC(18,2)` | Matches Oracle's numeric precision perfectly. |
| `VARCHAR2(255 CHAR)` | `VARCHAR(255)` | Native string array handling. |
| `DATE` | `TIMESTAMP WITHOUT TIME ZONE` | Mapped to preserve precise historical times. |
| `CLOB` | `TEXT` | Native PostgreSQL arbitrary-length character block. |

### Target Database Initialization Script (PostgreSQL Target)
```sql
-- Target Schema Space Initialization
CREATE SCHEMA IF NOT EXISTS erp_production;

-- Table 1: Customer Master Table
CREATE TABLE erp_production.customer_master (
    customer_id SERIAL PRIMARY KEY,
    customer_name VARCHAR(255) NOT NULL,
    email_address VARCHAR(150) UNIQUE,
    account_created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    account_status_code VARCHAR(10)
);

-- Table 2: Order Ledger Ledger Module
CREATE TABLE erp_production.order_ledger (
    order_id BIGSERIAL PRIMARY KEY,
    customer_id INT NOT NULL,
    order_timestamp TIMESTAMP WITHOUT TIME ZONE NOT NULL,
    gross_amount NUMERIC(18,2) NOT NULL,
    tax_amount NUMERIC(18,2) NOT NULL,
    order_payload TEXT,
    CONSTRAINT fk_ledger_customer FOREIGN KEY (customer_id) 
        REFERENCES erp_production.customer_master(customer_id) ON CONFLICT DO NOTHING
);
```

---

## 🔒 Phase 2: Role & User Privilege Provisioning (PostgreSQL Model)

PostgreSQL segregates users as cluster-wide roles. Here is the security mapping model:

```sql
-- Create distinct access management roles
CREATE ROLE app_admin WITH LOGIN PASSWORD 'SecurePostgresAdmin2026!';
CREATE ROLE app_read WITH LOGIN PASSWORD 'SecurePostgresRead2026!';
CREATE ROLE app_write WITH LOGIN PASSWORD 'SecurePostgresWrite2026!';

-- Assign explicit schema-level execution privileges
GRANT USAGE ON SCHEMA erp_production TO app_admin, app_read, app_write;

GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA erp_production TO app_admin;
GRANT SELECT ON ALL TABLES IN SCHEMA erp_production TO app_read;
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA erp_production TO app_write;
```

---

## 🧠 Phase 3: PL/pgSQL Code Blocks Transformation to PostgreSQL Syntax

### 1. Stored Procedure Transformation
*   **Oracle Source:** Mapped cleanly using PostgreSQL's native procedural engine Language `plpgsql`.

```sql
CREATE OR REPLACE PROCEDURE erp_production.sp_process_daily_settlement(p_target_date TIMESTAMP)
LANGUAGE plpgsql
AS \[ DECLARE     v_transaction_count INT := 0; BEGIN     -- Evaluate execution log counts     SELECT COUNT(*) INTO v_transaction_count      FROM erp_production.order_ledger      WHERE order_timestamp::DATE = p_target_date::DATE;          -- Apply updates across boundaries if data footprints exist     IF v_transaction_count > 0 THEN         UPDATE erp_production.customer_master c         SET account_status_code = 'ACTIVE'         WHERE c.customer_id IN (             SELECT o.customer_id              FROM erp_production.order_ledger o              WHERE o.order_timestamp::DATE = p_target_date::DATE         );     END IF; END; \];
```

### 2. Custom Function Transformation
```sql
CREATE OR REPLACE FUNCTION erp_production.fn_calculate_tax_variance(
    gross_amt NUMERIC, 
    tax_rate NUMERIC
)
RETURNS NUMERIC
LANGUAGE plpgsql
AS \[ DECLARE     v_calculated_variance NUMERIC(18,2); BEGIN     v_calculated_variance := gross_amt * (tax_rate / 100.00);     RETURN v_calculated_variance; END; \];
```
