#!/bin/bash

# Default backup directory is /var/backups
BACKUP_DIR="/var/backups"
LOG_FILE="/var/log/backup_restore.log"

# Ensure the script runs as root
if [[ $EUID -ne 0 ]]; then
    echo "This script must be run as root." >&2
    exit 1
fi

# Check if /var/backups exists, create it if not
if [ ! -d "$BACKUP_DIR" ]; then
    echo "$BACKUP_DIR does not exist, creating it now..."
    mkdir -p "$BACKUP_DIR"
fi

# Log actions
log_action() {
    local action="$1"
    echo "$(date '+%Y-%m-%d %H:%M:%S') - $action" >> "$LOG_FILE"
}

# Display menu
display_menu() {
    echo -e "\033[1;34m============================================="
    echo "      Backup and Restore Automation Tool     "
    echo "============================================="
    echo "1. Backup Files"
    echo "2. Restore Files"
    echo "3. Encrypted Backup"
    echo "4. Encrypted Restore"
    echo "5. View Available Backups"
    echo "6. Apply Retention Policy"
    echo "7. Monitor Disk Space"
    echo "8. Exit"
    echo "============================================="
}

# Backup files function
backup_files() {
    echo "Choose files/directories to back up (comma-separated):"
    echo "/etc - System Configurations"
    echo "/var/log - System Logs"
    echo "/home - User Data"
    read -p "Enter paths (e.g., /etc,/var/log,/home): " paths
    timestamp=$(date "+%Y-%m-%d_%H-%M-%S")
    backup_file="$BACKUP_DIR/backup_$timestamp.tar.gz"

    # Validate the paths
    if [ -z "$paths" ]; then
        echo "Error: No directories specified for backup."
        return 1
    fi

    # Create the backup using tar
    echo "Starting backup..."
    tar -czf "$backup_file" $paths

    # Check if the backup was successful
    if [ $? -eq 0 ]; then
        echo "Backup completed: $backup_file."
        log_action "Backup completed: $backup_file."

        # Calculate the size of the backup
        backup_size=$(du -sh "$backup_file" | cut -f1)
        echo "Backup Size: $backup_size"
        log_action "Backup size: $backup_size."
    else
        echo "Error: Backup failed."
        return 1
    fi
}

# Restore files function
restore_files() {
    read -p "Enter the backup file to restore (e.g., /var/backups/backup_2025-01-07.tar.gz): " backup_file
    if [ -f "$backup_file" ]; then
        echo "Restoring backup from $backup_file..."
        tar -xzf "$backup_file" -C /
        echo "Backup restored from $backup_file."
        log_action "Restored backup from $backup_file."
    else
        echo "Error: Backup file does not exist."
        return 1
    fi
}

# View available backups
view_backups() {
    echo "Available backups in $BACKUP_DIR:"
    ls -lh "$BACKUP_DIR"
}

# Monitor disk space
monitor_disk_space() {
    echo "Monitoring disk space..."
    df -h
}

# Main menu loop
while true; do
    display_menu
    read -p "Enter your choice: " choice
    case $choice in
        1) backup_files ;;
        2) restore_files ;;
        3) echo "Encrypted Backup not implemented yet." ;;
        4) echo "Encrypted Restore not implemented yet." ;;
        5) view_backups ;;
        6) echo "Apply Retention Policy not implemented yet." ;;
        7) monitor_disk_space ;;
        8) exit 0 ;;
        *) echo "Invalid choice. Please try again." ;;
    esac
done

