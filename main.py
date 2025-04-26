import os
import shutil
import datetime
import subprocess
import winreg
import logging
from pathlib import Path


def setup_logging():
    """Set up logging to track script execution."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('nvidia_backup.log'),
            logging.StreamHandler()
        ]
    )


def get_nvidia_driver_info():
    """Retrieve NVIDIA driver version using nvidia-smi."""
    try:
        result = subprocess.run(['nvidia-smi', '--query-gpu=driver_version', '--format=csv'],
                                capture_output=True, text=True, check=True)
        driver_version = result.stdout.splitlines()[1].strip()
        logging.info(f"NVIDIA Driver Version: {driver_version}")
        return driver_version
    except subprocess.CalledProcessError as e:
        logging.error(f"Failed to retrieve NVIDIA driver info: {e}")
        return "Unknown"


def create_backup_directory():
    """Create a timestamped backup directory."""
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_dir = Path.home() / f"NVIDIA_Settings_Backup_{timestamp}"
    backup_dir.mkdir(parents=True, exist_ok=True)
    logging.info(f"Created backup directory: {backup_dir}")
    return backup_dir


def backup_nvidia_profile_files(backup_dir):
    """Copy NVIDIA profile configuration files from ProgramData."""
    src_dir = Path(os.getenv('PROGRAMDATA')) / "NVIDIA Corporation" / "Drs"
    if not src_dir.exists():
        logging.warning(f"NVIDIA profile directory not found: {src_dir}")
        return False

    dest_dir = backup_dir / "NVIDIA_Profiles"
    try:
        shutil.copytree(src_dir, dest_dir, dirs_exist_ok=True)
        logging.info(f"Backed up NVIDIA profile files to: {dest_dir}")
        return True
    except Exception as e:
        logging.error(f"Failed to back up NVIDIA profile files: {e}")
        return False


def backup_nvidia_registry_settings(backup_dir):
    """Export NVIDIA registry settings to a .reg file."""
    reg_key = r"Software\NVIDIA Corporation"
    reg_file = backup_dir / "nvidia_registry_backup.reg"

    try:
        # Export registry key using reg export command
        subprocess.run(['reg', 'export', f'HKCU\\{reg_key}', str(reg_file)],
                       capture_output=True, text=True, check=True)
        logging.info(f"Backed up NVIDIA registry settings to: {reg_file}")
        return True
    except subprocess.CalledProcessError as e:
        logging.error(f"Failed to back up NVIDIA registry settings: {e}")
        return False


def main():
    """Main function to back up NVIDIA driver settings."""
    setup_logging()
    logging.info("Starting NVIDIA driver settings backup process")

    # Get NVIDIA driver info
    driver_version = get_nvidia_driver_info()

    # Create backup directory
    backup_dir = create_backup_directory()

    # Back up NVIDIA profile files
    profile_backup_success = backup_nvidia_profile_files(backup_dir)

    # Back up NVIDIA registry settings
    registry_backup_success = backup_nvidia_registry_settings(backup_dir)

    # Summary
    if profile_backup_success and registry_backup_success:
        logging.info(f"Backup completed successfully. Files saved to: {backup_dir}")
        print(f"\nBackup completed! Files saved to: {backup_dir}")
        print(
            "Please manually document display settings (e.g., resolution, refresh rate, HDR) as they are not included.")
    else:
        logging.warning("Backup partially failed. Check log for details.")
        print("\nBackup partially failed. Check nvidia_backup.log for details.")

    # Save driver info to a text file
    with open(backup_dir / "driver_info.txt", "w") as f:
        f.write(f"NVIDIA Driver Version: {driver_version}\n")
        f.write(f"Backup Date: {datetime.datetime.now()}\n")
        f.write(f"System: Windows 11 Pro 64-bit (Build 26100)\n")
        f.write(f"GPU: NVIDIA GeForce RTX 4070 Ti SUPER\n")

    print("\nNext steps:")
    print("- Verify the backup files in the directory.")
    print("- Consider copying the backup folder to an external drive or cloud storage.")
    print("- To restore, manually import the .reg file and copy profile files back (see documentation).")


if __name__ == "__main__":
    main()