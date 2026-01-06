#!/usr/bin/env python3
"""
MiningTaxes with Discord Integration - Installation & Update Script
Handles installation, updates, and configuration for the MiningTaxes plugin
"""

import os
import sys
import subprocess
import shutil
import argparse
from datetime import datetime
from pathlib import Path

class MiningTaxesInstaller:
    REPO_URL = "https://github.com/Thrainkrilleve/miningtaxdiscordupdate.git"
    INSTALL_DIR_NAME = "aa-miningtaxes-discord"
    
    def __init__(self):
        self.home_dir = Path.home()
        self.install_dir = self.home_dir / self.INSTALL_DIR_NAME
        self.auth_path = self._detect_auth_path()
        
    def _detect_auth_path(self):
        """Detect Alliance Auth installation path"""
        aa_path = os.environ.get('AA_PATH')
        if aa_path:
            return Path(aa_path)
        elif (self.home_dir / "myauth").exists():
            return self.home_dir / "myauth"
        else:
            return self.home_dir / "myauth"  # Default
    
    def run_command(self, cmd, check=True, cwd=None, capture=True):
        """Run a shell command"""
        try:
            if capture:
                result = subprocess.run(
                    cmd,
                    shell=True,
                    check=check,
                    capture_output=True,
                    text=True,
                    cwd=cwd
                )
            else:
                result = subprocess.run(
                    cmd,
                    shell=True,
                    check=check,
                    cwd=cwd
                )
            return result
        except subprocess.CalledProcessError as e:
            if capture:
                print(f"✗ Error: {e.stderr}")
            else:
                print(f"✗ Command failed: {cmd}")
            if check:
                sys.exit(1)
            return None
    
    def print_header(self, text):
        """Print a formatted header"""
        print("\n" + "=" * 50)
        print(text)
        print("=" * 50 + "\n")
    
    def check_prerequisites(self):
        """Check if prerequisites are met"""
        # Check if running as root
        if os.geteuid() == 0:
            print("✗ Please do not run as root. Run as your allianceauth user.")
            sys.exit(1)
        
        # Check virtual environment
        venv = os.environ.get('VIRTUAL_ENV')
        if not venv:
            print("✗ Error: Virtual environment not activated!")
            print("\nPlease activate your Alliance Auth virtual environment first:")
            print("  source /home/allianceauth/venv/bin/activate")
            sys.exit(1)
        
        print(f"✓ Virtual environment: {venv}")
        return True
    
    def clone_or_update_repo(self):
        """Clone repository if new, or update if exists"""
        if self.install_dir.exists():
            print(f"📦 Updating existing installation at {self.install_dir}...")
            self.run_command("git pull", cwd=self.install_dir)
            print("✓ Repository updated")
        else:
            print(f"📦 Cloning MiningTaxes with Discord integration...")
            self.run_command(f"git clone {self.REPO_URL} {self.install_dir}")
            print(f"✓ Repository cloned to {self.install_dir}")
    
    def install_plugin(self):
        """Install the plugin using pip"""
        print("\n📦 Installing MiningTaxes plugin...")
        self.run_command(f"pip install -e {self.install_dir}")
        print("✓ Plugin installed")
    
    def install_dependencies(self):
        """Install required dependencies"""
        print("\n📦 Installing dependencies...")
        self.run_command("pip install django-celery-results")
        print("✓ Dependencies installed")
    
    def backup_settings(self):
        """Backup existing settings file"""
        settings_file = self.auth_path / "myauth" / "settings" / "local.py"
        
        if settings_file.exists():
            backup_name = f"{settings_file}.backup.{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            shutil.copy2(settings_file, backup_name)
            print(f"✓ Settings backed up to {backup_name}")
            return settings_file
        else:
            print(f"⚠ Warning: Settings file not found at {settings_file}")
            return None
    
    def show_configuration_instructions(self):
        """Display configuration instructions"""
        self.print_header("CONFIGURATION REQUIRED")
        
        print("Add the following to your local.py:\n")
        
        print("# 1. Installed Apps")
        print("INSTALLED_APPS += [")
        print("    'miningtaxes',")
        print("    'django_celery_results',")
        print("]\n")
        
        print("# 2. Celery Configuration")
        print("CELERY_RESULT_BACKEND = 'django-db'")
        print("CELERY_CACHE_BACKEND = 'django-cache'\n")
        
        print("# 3. Scheduled Tasks")
        print("from celery.schedules import crontab\n")
        print("CELERYBEAT_SCHEDULE['miningtaxes_update_daily'] = {")
        print("    'task': 'miningtaxes.tasks.update_daily',")
        print("    'schedule': crontab(minute=0, hour='1'),")
        print("}\n")
        print("CELERYBEAT_SCHEDULE['miningtaxes_notifications'] = {")
        print("    'task': 'miningtaxes.tasks.notify_taxes_due',")
        print("    'schedule': crontab(0, 0, day_of_month='2'),")
        print("}\n")
        print("CELERYBEAT_SCHEDULE['miningtaxes_apply_interest'] = {")
        print("    'task': 'miningtaxes.tasks.apply_interest',")
        print("    'schedule': crontab(0, 0, day_of_month='15'),")
        print("}\n")
        
        print("# 4. (Optional) Price Source Configuration")
        print("MININGTAXES_PRICE_METHOD = 'Fuzzwork'  # or 'Janice'")
        print("# MININGTAXES_PRICE_JANICE_API_KEY = 'your_key'  # if using Janice\n")
        
        print("# 5. (Optional) Discord Notifications")
        print("MININGTAXES_DISCORD_WEBHOOK_URL = 'https://discord.com/api/webhooks/...'")
        print("MININGTAXES_DISCORD_CORP_WEBHOOK_URL = 'https://discord.com/api/webhooks/...'")
        print("MININGTAXES_DISCORD_CORP_CHANNEL_ID = 1234567890\n")
        
        print("=" * 50)
    
    def run_migrations(self):
        """Run Django migrations"""
        print("\n🔧 Running migrations...")
        self.run_command("python manage.py migrate", cwd=self.auth_path, capture=False)
        print("✓ Migrations complete")
    
    def collect_static(self):
        """Collect static files"""
        print("\n🔧 Collecting static files...")
        self.run_command("python manage.py collectstatic --noinput", cwd=self.auth_path)
        print("✓ Static files collected")
    
    def preload_prices(self):
        """Preload ore prices"""
        print("\n🔧 Preloading ore prices (this may take a minute)...")
        self.run_command("python manage.py miningtaxes_preload_prices", cwd=self.auth_path, capture=False)
        print("✓ Prices preloaded")
    
    def show_restart_instructions(self):
        """Show service restart instructions"""
        self.print_header("RESTART SERVICES")
        print("Restart your Alliance Auth services:\n")
        print("  sudo systemctl restart myauth-gunicorn")
        print("  sudo systemctl restart myauth-worker")
        print("  sudo systemctl restart myauth-beat")
        print("\nOr if using supervisor:")
        print("  sudo supervisorctl restart myauth:")
    
    def show_next_steps(self):
        """Show next steps"""
        self.print_header("NEXT STEPS")
        print("1. Restart your Alliance Auth services (see above)")
        print("2. Log in to Alliance Auth admin panel")
        print("3. Navigate to MiningTaxes → Settings")
        print("4. Configure tax rates and interest rate")
        print("5. Add corp accountant characters")
        print("6. (Optional) Configure Discord settings in admin panel\n")
        print("📚 Documentation:")
        print(f"   {self.install_dir}/README.md")
        print(f"   {self.install_dir}/DISCORD_INTEGRATION.md")
        print(f"   {self.install_dir}/DISCORD_DM_GUIDE.md")
        print(f"   {self.install_dir}/DISCORD_QUICKSTART.md\n")
    
    def install(self, skip_config=False):
        """Run full installation"""
        self.print_header("MiningTaxes Installation\nwith Discord DM & Corp Summary Support")
        
        print("🔍 Checking prerequisites...")
        self.check_prerequisites()
        
        self.clone_or_update_repo()
        self.install_plugin()
        self.install_dependencies()
        
        print("\n💾 Backing up settings...")
        self.backup_settings()
        
        if not skip_config:
            self.show_configuration_instructions()
            input("\nPress Enter when you have updated your local.py...")
        
        self.run_migrations()
        self.collect_static()
        self.preload_prices()
        
        self.show_restart_instructions()
        self.show_next_steps()
        
        self.print_header("✓ Installation Complete!")
    
    def update(self):
        """Update existing installation"""
        self.print_header("MiningTaxes Update")
        
        print("🔍 Checking prerequisites...")
        self.check_prerequisites()
        
        if not self.install_dir.exists():
            print(f"✗ Error: Installation not found at {self.install_dir}")
            print("\nRun with 'install' command first:")
            print(f"  python3 {sys.argv[0]} install")
            sys.exit(1)
        
        self.clone_or_update_repo()
        self.install_plugin()
        self.run_migrations()
        self.collect_static()
        
        self.show_restart_instructions()
        
        self.print_header("✓ Update Complete!")
    
    def uninstall(self):
        """Uninstall the plugin"""
        self.print_header("MiningTaxes Uninstall")
        
        response = input(f"Are you sure you want to uninstall? This will remove {self.install_dir} [y/N]: ")
        if response.lower() != 'y':
            print("Uninstall cancelled.")
            return
        
        print("\n🗑️  Uninstalling plugin...")
        self.run_command("pip uninstall aa-miningtaxes -y", check=False)
        
        if self.install_dir.exists():
            print(f"🗑️  Removing {self.install_dir}...")
            shutil.rmtree(self.install_dir)
        
        print("\n⚠️  Remember to:")
        print("1. Remove miningtaxes from INSTALLED_APPS")
        print("2. Remove CELERYBEAT_SCHEDULE entries")
        print("3. Run: python manage.py migrate")
        print("4. Restart your services")
        
        self.print_header("✓ Uninstall Complete!")

def main():
    parser = argparse.ArgumentParser(
        description='MiningTaxes with Discord Integration - Installation & Update Script',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s install              Install MiningTaxes
  %(prog)s install --skip-config  Install without config prompt
  %(prog)s update               Update existing installation
  %(prog)s uninstall            Remove MiningTaxes

For more information, visit:
  https://github.com/Thrainkrilleve/miningtaxdiscordupdate
        """
    )
    
    parser.add_argument(
        'command',
        choices=['install', 'update', 'uninstall'],
        help='Command to execute'
    )
    
    parser.add_argument(
        '--skip-config',
        action='store_true',
        help='Skip configuration prompt (install only)'
    )
    
    args = parser.parse_args()
    
    installer = MiningTaxesInstaller()
    
    try:
        if args.command == 'install':
            installer.install(skip_config=args.skip_config)
        elif args.command == 'update':
            installer.update()
        elif args.command == 'uninstall':
            installer.uninstall()
    except KeyboardInterrupt:
        print("\n\n✗ Cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n✗ Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
