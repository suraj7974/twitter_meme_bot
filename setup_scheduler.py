import os
import subprocess
import sys
from pathlib import Path
from crontab import CronTab


def create_virtual_environment():
    """Create a virtual environment and install required packages"""
    base_path = Path(__file__).parent.absolute()
    venv_path = base_path / 'venv'

    print("Creating virtual environment...")
    subprocess.run([sys.executable, '-m', 'venv', str(venv_path)], check=True)

    pip_path = venv_path / 'bin' / 'pip'

    print("Installing required packages...")
    requirements = [
        'python-dotenv',
        'groq',
        'tweepy',
        'pillow',
        'requests',
        'python-crontab'
    ]

    for package in requirements:
        print(f"Installing {package}...")
        subprocess.run([str(pip_path), 'install', package], check=True)

    return venv_path


def setup_cron_jobs(venv_path):
    """Set up cron jobs for running the scripts periodically"""
    cron = CronTab(user=True)

    cron.remove_all(comment='meme_poster')
    cron.remove_all(comment='text_poster')

    base_path = Path(__file__).parent.absolute()
    main_script = base_path / 'main.py'
    text_script = base_path / 'only_post.py'
    log_dir = base_path / 'logs'

    if not main_script.exists() or not text_script.exists():
        raise FileNotFoundError("Required script files not found")

    venv_python = venv_path / 'bin' / 'python'

    # Create jobs with output logging
    main_job = cron.new(
        command=f'{venv_python} {main_script} >> {log_dir}/main.log 2>&1',
        comment='meme_poster'
    )
    main_job.hour.every(6)

    text_job = cron.new(
        command=f'{venv_python} {text_script} >> {log_dir}/text.log 2>&1',
        comment='text_poster'
    )
    text_job.hour.every(2)

    # Write the jobs to crontab
    cron.write()

    print("\nCron jobs have been set up successfully:")
    print(f"Main script ({main_script}) will run every 6 hours")
    print(f"Text script ({text_script}) will run every 2 hours")
    print(f"Logs will be written to {log_dir}")


def create_log_directory():
    """Create a directory for log files"""
    log_dir = Path('logs')
    log_dir.mkdir(exist_ok=True)
    return log_dir


def main():
    try:

        print("Setting up virtual environment...")
        venv_path = create_virtual_environment()
        print("Virtual environment created successfully!")

        print("\nCreating logs directory...")
        log_dir = create_log_directory()
        print("Logs directory created successfully!")

        print("\nSetting up cron jobs...")
        setup_cron_jobs(venv_path)

        print("\nSetup completed successfully!")
        print("You can check the logs in the 'logs' directory")
        print("To view your cron jobs, run: crontab -l")

    except subprocess.CalledProcessError as e:
        print(f"Error during setup: {str(e)}")
        exit(1)
    except Exception as e:
        print(f"Error: {str(e)}")
        exit(1)


if __name__ == "__main__":
    main()
