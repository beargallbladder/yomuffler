-- Ford Bayesian Risk Score Engine - Database Schema
-- This script initializes the PostgreSQL database with all necessary tables and indexes

-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_stat_statements";

-- Create database (if running as superuser)
-- CREATE DATABASE ford_risk OWNER postgres;

-- Connect to the database
\c ford_risk;

-- Create schemas
CREATE SCHEMA IF NOT EXISTS risk_scoring;
CREATE SCHEMA IF NOT EXISTS swarm_management;
CREATE SCHEMA IF NOT EXISTS monitoring;

-- Set search path
SET search_path TO risk_scoring, swarm_management, monitoring, public;

-- ============================================================================
-- RISK SCORING TABLES
-- ============================================================================

-- Vehicle Risk Scores (Main results table)
CREATE TABLE IF NOT EXISTS risk_scoring.vehicle_risk_scores (
    vin VARCHAR(17) PRIMARY KEY,
    risk_score DECIMAL(5,4) NOT NULL CHECK (risk_score >= 0 AND risk_score <= 1),
    severity_bucket VARCHAR(20) NOT NULL CHECK (severity_bucket IN ('Low', 'Moderate', 'High', 'Critical', 'Severe')),
    cohort VARCHAR(100) NOT NULL,
    dominant_stressors JSONB NOT NULL DEFAULT '[]',
    recommended_action TEXT NOT NULL,
    revenue_opportunity DECIMAL(10,2) NOT NULL DEFAULT 0,
    confidence DECIMAL(5,4) NOT NULL CHECK (confidence >= 0 AND confidence <= 1),
    scored_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT (CURRENT_TIMESTAMP + INTERVAL '24 hours'),
    model_version VARCHAR(10) NOT NULL DEFAULT '1.0',
    prior_failure_rate DECIMAL(5,4) NOT NULL,
    data_freshness_hours INTEGER NOT NULL DEFAULT 0,
    calculation_time_ms DECIMAL(8,3) NOT NULL DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Vehicle Input Data (Raw telemetry data)
CREATE TABLE IF NOT EXISTS risk_scoring.vehicle_input_data (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    vin VARCHAR(17) NOT NULL,
    soc_30day_trend DECIMAL(5,4) NOT NULL CHECK (soc_30day_trend >= -1 AND soc_30day_trend <= 0),
    trip_cycles_weekly INTEGER NOT NULL CHECK (trip_cycles_weekly >= 0 AND trip_cycles_weekly <= 200),
    odometer_variance DECIMAL(5,4) NOT NULL CHECK (odometer_variance >= 0 AND odometer_variance <= 1),
    climate_stress_index DECIMAL(5,4) NOT NULL CHECK (climate_stress_index >= 0 AND climate_stress_index <= 1),
    maintenance_compliance DECIMAL(5,4) NOT NULL CHECK (maintenance_compliance >= 0 AND maintenance_compliance <= 1),
    cohort_model VARCHAR(50) NOT NULL,
    cohort_powertrain VARCHAR(20) NOT NULL,
    cohort_region VARCHAR(20) NOT NULL,
    cohort_mileage_band VARCHAR(20) NOT NULL,
    data_timestamp TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Bayesian Priors (Industry benchmarks)
CREATE TABLE IF NOT EXISTS risk_scoring.bayesian_priors (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    cohort_key VARCHAR(100) NOT NULL UNIQUE,
    base_failure_rate DECIMAL(5,4) NOT NULL CHECK (base_failure_rate >= 0 AND base_failure_rate <= 1),
    sample_size INTEGER NOT NULL CHECK (sample_size > 0),
    confidence_interval_lower DECIMAL(5,4) NOT NULL,
    confidence_interval_upper DECIMAL(5,4) NOT NULL,
    source VARCHAR(50) NOT NULL,
    study_year INTEGER,
    last_updated TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Likelihood Ratios (Ford historical data)
CREATE TABLE IF NOT EXISTS risk_scoring.likelihood_ratios (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    stressor_type VARCHAR(50) NOT NULL,
    given_failure DECIMAL(5,4) NOT NULL CHECK (given_failure >= 0 AND given_failure <= 1),
    given_no_failure DECIMAL(5,4) NOT NULL CHECK (given_no_failure >= 0 AND given_no_failure <= 1),
    likelihood_ratio DECIMAL(8,4) NOT NULL,
    sample_size_failure INTEGER NOT NULL,
    sample_size_no_failure INTEGER NOT NULL,
    confidence_level DECIMAL(5,4) NOT NULL DEFAULT 0.95,
    last_updated TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(stressor_type)
);

-- ============================================================================
-- SWARM MANAGEMENT TABLES
-- ============================================================================

-- Processing Tasks
CREATE TABLE IF NOT EXISTS swarm_management.processing_tasks (
    task_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    task_type VARCHAR(50) NOT NULL,
    vin VARCHAR(17) NOT NULL,
    input_data JSONB NOT NULL,
    priority INTEGER NOT NULL DEFAULT 1 CHECK (priority >= 1 AND priority <= 5),
    status VARCHAR(20) NOT NULL DEFAULT 'pending' CHECK (status IN ('pending', 'processing', 'completed', 'failed', 'cancelled')),
    worker_id VARCHAR(100),
    result JSONB,
    error_message TEXT,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    started_at TIMESTAMP WITH TIME ZONE,
    completed_at TIMESTAMP WITH TIME ZONE,
    processing_time_ms DECIMAL(10,3)
);

-- Swarm Worker Status
CREATE TABLE IF NOT EXISTS swarm_management.swarm_worker_status (
    worker_id VARCHAR(100) PRIMARY KEY,
    service_type VARCHAR(50) NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'idle' CHECK (status IN ('idle', 'busy', 'offline', 'error', 'scaling_up', 'scaling_down')),
    current_task_id UUID REFERENCES swarm_management.processing_tasks(task_id),
    last_heartbeat TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    processed_count INTEGER NOT NULL DEFAULT 0,
    error_count INTEGER NOT NULL DEFAULT 0,
    avg_processing_time_ms DECIMAL(10,3) NOT NULL DEFAULT 0,
    cpu_usage_percent DECIMAL(5,2) NOT NULL DEFAULT 0,
    memory_usage_mb DECIMAL(10,2) NOT NULL DEFAULT 0,
    queue_depth INTEGER NOT NULL DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Batch Processing Jobs
CREATE TABLE IF NOT EXISTS swarm_management.batch_jobs (
    batch_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    total_vins INTEGER NOT NULL,
    processed_vins INTEGER NOT NULL DEFAULT 0,
    status VARCHAR(20) NOT NULL DEFAULT 'queued' CHECK (status IN ('queued', 'processing', 'completed', 'failed', 'cancelled')),
    priority INTEGER NOT NULL DEFAULT 1 CHECK (priority >= 1 AND priority <= 5),
    callback_url TEXT,
    estimated_completion_time TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    started_at TIMESTAMP WITH TIME ZONE,
    completed_at TIMESTAMP WITH TIME ZONE,
    error_message TEXT
);

-- ============================================================================
-- MONITORING TABLES
-- ============================================================================

-- Processing History (Audit trail)
CREATE TABLE IF NOT EXISTS monitoring.processing_history (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    vin VARCHAR(17) NOT NULL,
    task_id UUID,
    worker_id VARCHAR(100),
    processing_time_ms DECIMAL(10,3) NOT NULL,
    status VARCHAR(20) NOT NULL,
    error_message TEXT,
    risk_score DECIMAL(5,4),
    severity_bucket VARCHAR(20),
    model_version VARCHAR(10),
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP WITH TIME ZONE
);

-- System Metrics
CREATE TABLE IF NOT EXISTS monitoring.system_metrics (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    metric_name VARCHAR(100) NOT NULL,
    metric_value DECIMAL(15,4) NOT NULL,
    metric_type VARCHAR(20) NOT NULL CHECK (metric_type IN ('counter', 'gauge', 'histogram', 'summary')),
    labels JSONB DEFAULT '{}',
    timestamp TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- API Request Logs
CREATE TABLE IF NOT EXISTS monitoring.api_request_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    request_id UUID NOT NULL,
    endpoint VARCHAR(200) NOT NULL,
    method VARCHAR(10) NOT NULL,
    status_code INTEGER NOT NULL,
    processing_time_ms DECIMAL(10,3) NOT NULL,
    cached BOOLEAN NOT NULL DEFAULT FALSE,
    user_agent TEXT,
    ip_address INET,
    vin VARCHAR(17),
    error_message TEXT,
    timestamp TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================================
-- INDEXES FOR PERFORMANCE
-- ============================================================================

-- Vehicle Risk Scores Indexes
CREATE INDEX IF NOT EXISTS idx_vehicle_risk_scores_severity ON risk_scoring.vehicle_risk_scores(severity_bucket);
CREATE INDEX IF NOT EXISTS idx_vehicle_risk_scores_cohort ON risk_scoring.vehicle_risk_scores(cohort);
CREATE INDEX IF NOT EXISTS idx_vehicle_risk_scores_scored_at ON risk_scoring.vehicle_risk_scores(scored_at);
CREATE INDEX IF NOT EXISTS idx_vehicle_risk_scores_expires_at ON risk_scoring.vehicle_risk_scores(expires_at);
CREATE INDEX IF NOT EXISTS idx_vehicle_risk_scores_risk_score ON risk_scoring.vehicle_risk_scores(risk_score DESC);

-- Vehicle Input Data Indexes
CREATE INDEX IF NOT EXISTS idx_vehicle_input_data_vin ON risk_scoring.vehicle_input_data(vin);
CREATE INDEX IF NOT EXISTS idx_vehicle_input_data_timestamp ON risk_scoring.vehicle_input_data(data_timestamp);
CREATE INDEX IF NOT EXISTS idx_vehicle_input_data_cohort ON risk_scoring.vehicle_input_data(cohort_model, cohort_powertrain, cohort_region, cohort_mileage_band);

-- Processing Tasks Indexes
CREATE INDEX IF NOT EXISTS idx_processing_tasks_status ON swarm_management.processing_tasks(status);
CREATE INDEX IF NOT EXISTS idx_processing_tasks_vin ON swarm_management.processing_tasks(vin);
CREATE INDEX IF NOT EXISTS idx_processing_tasks_worker_id ON swarm_management.processing_tasks(worker_id);
CREATE INDEX IF NOT EXISTS idx_processing_tasks_created_at ON swarm_management.processing_tasks(created_at);
CREATE INDEX IF NOT EXISTS idx_processing_tasks_priority ON swarm_management.processing_tasks(priority DESC, created_at);

-- Swarm Worker Status Indexes
CREATE INDEX IF NOT EXISTS idx_swarm_worker_status_service_type ON swarm_management.swarm_worker_status(service_type);
CREATE INDEX IF NOT EXISTS idx_swarm_worker_status_status ON swarm_management.swarm_worker_status(status);
CREATE INDEX IF NOT EXISTS idx_swarm_worker_status_last_heartbeat ON swarm_management.swarm_worker_status(last_heartbeat);

-- Monitoring Indexes
CREATE INDEX IF NOT EXISTS idx_processing_history_vin ON monitoring.processing_history(vin);
CREATE INDEX IF NOT EXISTS idx_processing_history_created_at ON monitoring.processing_history(created_at);
CREATE INDEX IF NOT EXISTS idx_processing_history_worker_id ON monitoring.processing_history(worker_id);

CREATE INDEX IF NOT EXISTS idx_system_metrics_name_timestamp ON monitoring.system_metrics(metric_name, timestamp);
CREATE INDEX IF NOT EXISTS idx_system_metrics_timestamp ON monitoring.system_metrics(timestamp);

CREATE INDEX IF NOT EXISTS idx_api_request_logs_timestamp ON monitoring.api_request_logs(timestamp);
CREATE INDEX IF NOT EXISTS idx_api_request_logs_endpoint ON monitoring.api_request_logs(endpoint);
CREATE INDEX IF NOT EXISTS idx_api_request_logs_status_code ON monitoring.api_request_logs(status_code);

-- ============================================================================
-- TRIGGERS FOR AUTOMATIC UPDATES
-- ============================================================================

-- Function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Apply update triggers
CREATE TRIGGER update_vehicle_risk_scores_updated_at 
    BEFORE UPDATE ON risk_scoring.vehicle_risk_scores 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_swarm_worker_status_updated_at 
    BEFORE UPDATE ON swarm_management.swarm_worker_status 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- ============================================================================
-- INITIAL DATA POPULATION
-- ============================================================================

-- Insert Bayesian Priors from Argon National Study (2015)
INSERT INTO risk_scoring.bayesian_priors (cohort_key, base_failure_rate, sample_size, confidence_interval_lower, confidence_interval_upper, source, study_year) VALUES
('F150|ICE|NORTH|LOW', 0.023, 15420, 0.021, 0.025, 'Argon National Study', 2015),
('F150|ICE|NORTH|MEDIUM', 0.031, 12850, 0.028, 0.034, 'Argon National Study', 2015),
('F150|ICE|NORTH|HIGH', 0.045, 8930, 0.041, 0.049, 'Argon National Study', 2015),
('F150|ICE|SOUTH|LOW', 0.034, 11200, 0.031, 0.037, 'Argon National Study', 2015),
('F150|ICE|SOUTH|MEDIUM', 0.042, 9800, 0.038, 0.046, 'Argon National Study', 2015),
('F150|ICE|SOUTH|HIGH', 0.058, 6750, 0.053, 0.063, 'Argon National Study', 2015),
('F150|HYBRID|NORTH|LOW', 0.019, 3420, 0.016, 0.022, 'Argon National Study', 2015),
('F150|HYBRID|NORTH|MEDIUM', 0.027, 2850, 0.023, 0.031, 'Argon National Study', 2015),
('F150|HYBRID|NORTH|HIGH', 0.039, 1930, 0.034, 0.044, 'Argon National Study', 2015),
('EXPLORER|ICE|NORTH|LOW', 0.021, 8420, 0.019, 0.023, 'Argon National Study', 2015),
('EXPLORER|ICE|NORTH|MEDIUM', 0.029, 7250, 0.026, 0.032, 'Argon National Study', 2015),
('EXPLORER|ICE|NORTH|HIGH', 0.041, 4930, 0.037, 0.045, 'Argon National Study', 2015),
('MUSTANG|ICE|NORTH|LOW', 0.018, 5420, 0.016, 0.020, 'Argon National Study', 2015),
('MUSTANG|ICE|NORTH|MEDIUM', 0.025, 4650, 0.022, 0.028, 'Argon National Study', 2015),
('MUSTANG|ICE|NORTH|HIGH', 0.037, 2930, 0.033, 0.041, 'Argon National Study', 2015),
('TRANSIT|ICE|COMMERCIAL|LOW', 0.052, 3420, 0.047, 0.057, 'Argon National Study', 2015),
('TRANSIT|ICE|COMMERCIAL|MEDIUM', 0.067, 2850, 0.061, 0.073, 'Argon National Study', 2015),
('TRANSIT|ICE|COMMERCIAL|HIGH', 0.089, 1930, 0.081, 0.097, 'Argon National Study', 2015)
ON CONFLICT (cohort_key) DO NOTHING;

-- Insert Likelihood Ratios from Ford Historical Data
INSERT INTO risk_scoring.likelihood_ratios (stressor_type, given_failure, given_no_failure, likelihood_ratio, sample_size_failure, sample_size_no_failure) VALUES
('soc_decline', 0.78, 0.12, 6.50, 2340, 47680),
('trip_cycling', 0.65, 0.23, 2.83, 2340, 47680),
('climate_stress', 0.43, 0.18, 2.39, 2340, 47680),
('maintenance_skip', 0.67, 0.31, 2.16, 2340, 47680)
ON CONFLICT (stressor_type) DO UPDATE SET
    given_failure = EXCLUDED.given_failure,
    given_no_failure = EXCLUDED.given_no_failure,
    likelihood_ratio = EXCLUDED.likelihood_ratio,
    sample_size_failure = EXCLUDED.sample_size_failure,
    sample_size_no_failure = EXCLUDED.sample_size_no_failure,
    last_updated = CURRENT_TIMESTAMP;

-- ============================================================================
-- VIEWS FOR COMMON QUERIES
-- ============================================================================

-- High Risk Vehicles View
CREATE OR REPLACE VIEW risk_scoring.high_risk_vehicles AS
SELECT 
    vin,
    risk_score,
    severity_bucket,
    cohort,
    recommended_action,
    revenue_opportunity,
    scored_at,
    expires_at
FROM risk_scoring.vehicle_risk_scores
WHERE severity_bucket IN ('High', 'Critical', 'Severe')
    AND expires_at > CURRENT_TIMESTAMP
ORDER BY risk_score DESC;

-- Swarm Health View
CREATE OR REPLACE VIEW swarm_management.swarm_health AS
SELECT 
    service_type,
    COUNT(*) as total_workers,
    COUNT(*) FILTER (WHERE status = 'idle') as idle_workers,
    COUNT(*) FILTER (WHERE status = 'busy') as busy_workers,
    COUNT(*) FILTER (WHERE status = 'offline') as offline_workers,
    COUNT(*) FILTER (WHERE status = 'error') as error_workers,
    AVG(cpu_usage_percent) as avg_cpu_usage,
    AVG(memory_usage_mb) as avg_memory_usage,
    SUM(processed_count) as total_processed,
    SUM(error_count) as total_errors
FROM swarm_management.swarm_worker_status
GROUP BY service_type;

-- Processing Performance View
CREATE OR REPLACE VIEW monitoring.processing_performance AS
SELECT 
    DATE_TRUNC('hour', created_at) as hour,
    COUNT(*) as total_requests,
    COUNT(*) FILTER (WHERE status = 'completed') as successful_requests,
    COUNT(*) FILTER (WHERE status = 'failed') as failed_requests,
    AVG(processing_time_ms) as avg_processing_time_ms,
    PERCENTILE_CONT(0.95) WITHIN GROUP (ORDER BY processing_time_ms) as p95_processing_time_ms
FROM monitoring.processing_history
WHERE created_at >= CURRENT_TIMESTAMP - INTERVAL '24 hours'
GROUP BY DATE_TRUNC('hour', created_at)
ORDER BY hour DESC;

-- ============================================================================
-- CLEANUP PROCEDURES
-- ============================================================================

-- Function to clean up expired risk scores
CREATE OR REPLACE FUNCTION cleanup_expired_risk_scores()
RETURNS INTEGER AS $$
DECLARE
    deleted_count INTEGER;
BEGIN
    DELETE FROM risk_scoring.vehicle_risk_scores 
    WHERE expires_at < CURRENT_TIMESTAMP;
    
    GET DIAGNOSTICS deleted_count = ROW_COUNT;
    
    INSERT INTO monitoring.system_metrics (metric_name, metric_value, metric_type)
    VALUES ('cleanup_expired_risk_scores', deleted_count, 'counter');
    
    RETURN deleted_count;
END;
$$ LANGUAGE plpgsql;

-- Function to clean up old processing history
CREATE OR REPLACE FUNCTION cleanup_old_processing_history(retention_days INTEGER DEFAULT 30)
RETURNS INTEGER AS $$
DECLARE
    deleted_count INTEGER;
BEGIN
    DELETE FROM monitoring.processing_history 
    WHERE created_at < CURRENT_TIMESTAMP - (retention_days || ' days')::INTERVAL;
    
    GET DIAGNOSTICS deleted_count = ROW_COUNT;
    
    INSERT INTO monitoring.system_metrics (metric_name, metric_value, metric_type)
    VALUES ('cleanup_old_processing_history', deleted_count, 'counter');
    
    RETURN deleted_count;
END;
$$ LANGUAGE plpgsql;

-- Grant permissions
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA risk_scoring TO postgres;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA swarm_management TO postgres;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA monitoring TO postgres;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA risk_scoring TO postgres;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA swarm_management TO postgres;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA monitoring TO postgres;

-- Create application user (uncomment if needed)
-- CREATE USER ford_risk_app WITH PASSWORD 'secure_password';
-- GRANT CONNECT ON DATABASE ford_risk TO ford_risk_app;
-- GRANT USAGE ON SCHEMA risk_scoring, swarm_management, monitoring TO ford_risk_app;
-- GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA risk_scoring, swarm_management, monitoring TO ford_risk_app;
-- GRANT USAGE ON ALL SEQUENCES IN SCHEMA risk_scoring, swarm_management, monitoring TO ford_risk_app;

COMMIT; 