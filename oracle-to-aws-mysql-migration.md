# Playbook 1: Relational Schema Migration (Oracle 19c On-Premise to AWS RDS MySQL 8.x)

This production playbook outlines the operational steps and conversion architecture required to safely migrate a critical corporate schema module from an on-premise Oracle 19c database over to an AWS RDS MySQL environment.

## 📊 Source Environment Topology
*   **Database Engine:** Oracle Database 19c Enterprise Edition
*   **Schema Footprint:** 1 Target Schema
*   **Storage Profiles:** 1 Dedicated Tablespace (`DATA_TS01`)
*   **Access Control Layer:** 3 Database Users (`app_admin`, `app_read`, `app_write`)
*   **Data Layer Objects:** 2 Core Transactional Tables (`customer_master`, `order_ledger`)
*   **Business Logic Units:** 1 PL/SQL Stored Procedure (`sp_process_daily_settlement`), 1 Custom Function (`fn_calculate_tax_variance`)

---

## 🛠️ Phase 1: Structural Schema & Target Data Type Mapping

Oracle's proprietary PL/SQL data architecture must be carefully re-mapped to fit MySQL's relational processing standards:

| Oracle 19c Data Type | AWS RDS MySQL 8.x Target Type | Migration Strategy / Handling Note |
| :--- | :--- | :--- |
| `NUMBER(10,0)` | `INT` or `BIGINT` | Standard integer transition. |
| `NUMBER(18,2)` | `DECIMAL(18,2)` | Maintained for absolute financial precision. |
| `VARCHAR2(255 CHAR)` | `VARCHAR(255)` | UTF-8 default character collation enforcement. |
| `DATE` | `DATETIME` | Oracle `DATE` carries timestamps; mapped to `DATETIME`. |
| `CLOB` | `LONGTEXT` | Large text object storage block mapping. |

### Target Database Initialization Script (MySQL Target)
```sql
-- Target Schema Initialization
CREATE DATABASE IF NOT EXISTS app_production_erp;
USE app_production_erp;

-- Table 1: Customer Master Data Structure
CREATE TABLE customer_master (
    customer_id INT NOT NULL AUTO_INCREMENT,
    customer_name VARCHAR(255) NOT NULL,
    email_address VARCHAR(150) UNIQUE,
    account_created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    account_status_code VARCHAR(10),
    PRIMARY KEY (customer_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Table 2: Order Ledger Ledger Module
CREATE TABLE order_ledger (
    order_id BIGINT NOT NULL AUTO_INCREMENT,
    customer_id INT NOT NULL,
    order_timestamp DATETIME NOT NULL,
    gross_amount DECIMAL(18,2) NOT NULL,
    tax_amount DECIMAL(18,2) NOT NULL,
    order_payload LONGTEXT,
    PRIMARY KEY (order_id),
    CONSTRAINT fk_ledger_customer FOREIGN KEY (customer_id) 
        REFERENCES customer_master(customer_id) ON DELETE RESTRICT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
```

---

## 🔒 Phase 2: Role & User Privilege Provisioning (MySQL Model)

MySQL handles permissions at the hostname and database level rather than utilizing tablespaces. The 3 legacy Oracle users are provisioned as follows:

```sql
-- 1. Administrative Owner Role
CREATE USER 'app_admin'@'%' IDENTIFIED BY 'SecureAdminPass2026!';
GRANT ALL PRIVILEGES ON app_production_erp.* TO 'app_admin'@'%';

-- 2. Read-Only Reporting Client
CREATE USER 'app_read'@'%' IDENTIFIED BY 'SecureReadPass2026!';
GRANT SELECT ON app_production_erp.* TO 'app_read'@'%';

-- 3. Application Read/Write Client
CREATE USER 'app_write'@'%' IDENTIFIED BY 'SecureWritePass2026!';
GRANT SELECT, INSERT, UPDATE, DELETE ON app_production_erp.* TO 'app_write'@'%';

FLUSH PRIVILEGES;
```

---

## 🧠 Phase 3: PL/SQL Code Blocks Transformation to MySQL Syntax

### 1. Stored Procedure Transformation
*   **Oracle Source:** Relied on explicit cursor processing and proprietary exception blocks.
*   **MySQL Target Translation:** Re-engineered using standard `DETERMINISTIC` transaction frameworks.

```sql
DELIMITER \[  CREATE PROCEDURE sp_process_daily_settlement(IN target_date DATETIME) DETERMINISTIC BEGIN     -- Declare local execution variables     DECLARE transaction_count INT DEFAULT 0;          -- Transaction processing wrapper     START TRANSACTION;          SELECT COUNT(*) INTO transaction_count      FROM order_ledger      WHERE DATE(order_timestamp) = DATE(target_date);          -- Business logic processing block     IF transaction_count > 0 THEN         UPDATE customer_master c         INNER JOIN order_ledger o ON c.customer_id = o.customer_id         SET c.account_status_code = 'ACTIVE'         WHERE DATE(o.order_timestamp) = DATE(target_date);     END IF;          COMMIT; END\]

DELIMITER ;
```

### 2. Custom Function Transformation
```sql
DELIMITER \[  CREATE FUNCTION fn_calculate_tax_variance(gross_amt DECIMAL(18,2), tax_rate DECIMAL(4,2)) RETURNS DECIMAL(18,2) DETERMINISTIC BEGIN     DECLARE calculated_variance DECIMAL(18,2);     SET calculated_variance = gross_amt * (tax_rate / 100.00);     RETURN calculated_variance; END\]

DELIMITER ;
```
