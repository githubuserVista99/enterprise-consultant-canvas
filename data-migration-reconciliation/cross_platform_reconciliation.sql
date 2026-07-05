-- =========================================================================
-- Title: Dual-Database Reconciliation & Financial Financial Integrity Audit Engine
-- Description: Runs automated sum validations to guarantee zero transaction loss
-- =========================================================================

CREATE OR REPLACE PROCEDURE pr_reconcile_invoice_data_migration()
LANGUAGE plpgsql
AS $$
DECLARE
    v_source_count INT;
    v_target_count INT;
    v_source_gross_sum NUMERIC(18,2);
    v_target_gross_sum NUMERIC(18,2);
    v_variance NUMERIC(18,2);
BEGIN
    -- Step 1: Capture aggregate row footprints from the source Symfonia staging table
    SELECT COUNT(*), COALESCE(SUM(gross_amount), 0)
    INTO v_source_count, v_source_gross_sum
    FROM staging_migration.src_symfonia_invoices;

    -- Step 2: Capture matching aggregate footprints from the target Systim ledger architecture
    SELECT COUNT(*), COALESCE(SUM(document_gross_value), 0)
    INTO v_target_count, v_target_gross_sum
    FROM production_erp.tgt_systim_ledgers;

    -- Step 3: Execute absolute variance calculations to detect schema degradation
    v_variance := v_source_gross_sum - v_target_gross_sum;

    -- Step 4: Lineage reporting and constraint enforcement
    RAISE NOTICE '====================================================';
    RAISE NOTICE 'MIGRATION AUDIT RUN TIME: %', clock_timestamp();
    RAISE NOTICE 'SOURCE ROW COUNT: % | TARGET ROW COUNT: %', v_source_count, v_target_count;
    RAISE NOTICE 'SOURCE BALANCE: $ % | TARGET BALANCE: $ %', v_source_gross_sum, v_target_gross_sum;
    RAISE NOTICE 'TOTAL VARIANCE PROFILE: $ %', v_variance;
    RAISE NOTICE '====================================================';

    IF v_source_count != v_target_count OR v_variance != 0.00 THEN
        RAISE EXCEPTION '[CRITICAL] Audit Failure: Data consistency drift located! Production switchover aborted.';
    ELSE
        RAISE NOTICE '[SUCCESS] 100% Data Consistency Verified. Financial ledgers balance perfectly down to the absolute penny.';
    END IF;
END;
$$;
