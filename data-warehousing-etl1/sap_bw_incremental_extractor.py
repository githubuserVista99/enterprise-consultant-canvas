# =========================================================================
# Title: Incremental Change-Data-Capture (CDC) Extraction Pipeline Engine
# Description: Streamlines delta loads from REST endpoints & staging environments
# Author: Enterprise Data Architect (15+ Years Experience)
# =========================================================================

import os
import requests
import psycopg2
from datetime import datetime, timedelta

def extract_incremental_deltas():
    # Establish connection metrics for the unified target data warehouse
    conn = psycopg2.connect(
        host=os.getenv("DWH_HOST", "dwh-cluster-prod.internal"),
        database="enterprise_dwh",
        user="etl_pipeline_executor",
        password=os.getenv("DWH_PASS")
    )
    cursor = conn.cursor()
    
    # Step 1: Fetch the precise high-water mark (last successful load execution timestamp)
    cursor.execute("SELECT max(last_extracted_timestamp) FROM dw_governance.pipeline_logs WHERE status = 'SUCCESS'")
    last_hwm = cursor.fetchone()[0] or (datetime.utcnow() - timedelta(days=1))
    
    print(f"[INFO] Initializing ETL Delta Extraction from High-Water Mark: {last_hwm}")
    
    # Step 2: Query the operational REST API endpoint using localized high-water mark parameters
    endpoint_url = "https://source-system.internal"
    payload = {"delta_start": last_hwm.isoformat(), "batch_limit": 5000}
    
    try:
        response = requests.get(endpoint_url, params=payload, timeout=30)
        response.raise_for_status()
        records = response.json().get("data", [])
        
        # Step 3: Stream stage loads using bulk upsert statements to isolate analytical processes
        if records:
            upsert_query = """
                INSERT INTO dw_staging.stg_mis_records (record_id, source_system, metric_value, record_timestamp)
                VALUES (%s, %s, %s, %s)
                ON CONFLICT (record_id) DO UPDATE SET metric_value = EXCLUDED.metric_value;
            """
            batch_data = [(r['id'], r['source'], r['val'], r['ts']) for r in records]
            cursor.executemany(upsert_query, batch_data)
            
            # Log successful processing lineage
            cursor.execute(
                "INSERT INTO dw_governance.pipeline_logs (last_extracted_timestamp, status) VALUES (%s, 'SUCCESS')",
                (datetime.utcnow(),)
            )
            conn.commit()
            print(f"[SUCCESS] Extracted and staged {len(records)} delta source lineages securely.")
        else:
            print("[INFO] Zero new source increments located across target structures.")
            
    except Exception as e:
        conn.rollback()
        print(f"[CRITICAL] ETL Data Extraction Pipeline Crashed: {str(e)}")
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    extract_incremental_deltas()
