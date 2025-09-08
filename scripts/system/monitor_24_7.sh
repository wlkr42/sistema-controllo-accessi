#!/bin/bash
# Enterprise Monitoring Script for 24/7/365 Operation
# Monitors and auto-recovers Access Control System

LOG_FILE="/opt/access_control/logs/monitor_24_7.log"
HEALTH_URL="http://localhost:5000/api/health"
MAX_FAILURES=3
FAILURE_COUNT=0

# Function to log messages
log_message() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

# Function to check system health
check_health() {
    response=$(curl -s -f -m 5 "$HEALTH_URL" 2>/dev/null)
    return $?
}

# Function to restart service
restart_service() {
    log_message "WARNING: Restarting service..."
    systemctl restart access-control-web
    sleep 10
    
    if systemctl is-active --quiet access-control-web; then
        log_message "INFO: Service restarted successfully"
        FAILURE_COUNT=0
        return 0
    else
        log_message "ERROR: Service restart failed"
        return 1
    fi
}

# Function to check disk space
check_disk_space() {
    usage=$(df /opt/access_control | awk 'NR==2 {print int($5)}')
    if [ "$usage" -gt 90 ]; then
        log_message "WARNING: Disk usage at $usage%"
        # Clean old logs
        find /opt/access_control/logs -name "*.gz" -mtime +7 -delete
        find /opt/access_control/logs -name "*.1" -mtime +7 -delete
    fi
}

# Function to check database integrity
check_database() {
    if [ -f /opt/access_control/data/access.db ]; then
        size=$(stat -c%s "/opt/access_control/data/access.db")
        if [ "$size" -lt 1000 ]; then
            log_message "ERROR: Database file too small ($size bytes)"
            return 1
        fi
    else
        log_message "ERROR: Database file missing"
        return 1
    fi
    return 0
}

# Main monitoring loop
log_message "INFO: Monitor 24/7 started"

while true; do
    # Check if service is running
    if ! systemctl is-active --quiet access-control-web; then
        log_message "ERROR: Service not running"
        restart_service
    fi
    
    # Check health endpoint
    if ! check_health; then
        FAILURE_COUNT=$((FAILURE_COUNT + 1))
        log_message "WARNING: Health check failed ($FAILURE_COUNT/$MAX_FAILURES)"
        
        if [ "$FAILURE_COUNT" -ge "$MAX_FAILURES" ]; then
            log_message "ERROR: Max failures reached, restarting service"
            restart_service
        fi
    else
        FAILURE_COUNT=0
    fi
    
    # Check disk space every 10 minutes
    if [ $(($(date +%s) % 600)) -lt 60 ]; then
        check_disk_space
    fi
    
    # Check database
    if ! check_database; then
        log_message "ERROR: Database check failed"
        # Don't restart for database issues, just alert
    fi
    
    # Check memory usage
    mem_usage=$(free | grep Mem | awk '{print int($3/$2 * 100)}')
    if [ "$mem_usage" -gt 85 ]; then
        log_message "WARNING: Memory usage at $mem_usage%"
        if [ "$mem_usage" -gt 95 ]; then
            log_message "CRITICAL: Memory critically high, restarting service"
            restart_service
        fi
    fi
    
    # Sleep before next check
    sleep 60
done