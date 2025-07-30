import argparse
import json
import os
import re
import shutil
import subprocess
import sys
from contextlib import contextmanager
from typing import Any, Dict, Optional, Tuple

DEFAULT_API_REPO_URL = 'git@github.com:victorebouvie/python-portfolio-api.git'
DEFAULT_JSON_FILE_NAME = 'projects.json'
API_CLONE_DIR = 'temp_api_repo'
PROJECT_CLONE_DIR = 'temp_project_repo'

@contextmanager
def temporary_directories(*dirs: str):
    try:
        yield
    finally:
        for directory in dirs:
            if os.path.exists(directory):
                shutil.rmtree(directory, onerror=handle_remove_readonly)

def handle_remove_readonly(func, path, exc_info):
    """
    Handler for shutil.rmtree's onexc argument.
    Handles readonly errors on Windows.
    """
    exc_value = exc_info[1]
    if isinstance(exc_value, PermissionError):
        os.chmod(path, 0o777)
        func(path)
    else:
        raise

class PortfolioUpdater:
    def __init__(self, project_url: str, api_url: str, json_file: str):
        self.project_repo_url = project_url
        self.api_repo_url = api_url
        self.json_file_name = json_file

    def _run_command(self, command: list[str], working_dir: str = '.') -> bool:
        try:
            subprocess.run(
                command, check=True, cwd=working_dir, capture_output=True, text=True, encoding='utf-8'
            )
            return True
        except subprocess.CalledProcessError:
            print(f"Error executing command: {' '.join(command)}", file=sys.stderr)
            return False

    def _clone_repo(self, repo_url: str, clone_dir: str) -> bool:
        if os.path.exists(clone_dir):
            shutil.rmtree(clone_dir)
        
        command = ['git', 'clone', repo_url, clone_dir]
        return self._run_command(command)

    def _parse_readme(self) -> Optional[Dict[str, Any]]:
        readme_path = os.path.join(PROJECT_CLONE_DIR, 'README.md')
        if not os.path.exists(readme_path):
            return None

        with open(readme_path, 'r', encoding='utf-8') as file:
            content = file.read()

        name_match = re.search(r'^#\s(.+)', content, re.MULTILINE)
        desc_match = re.search(r'##\s(?:📖\s)?About The Project\n\n(.*?)\n\n---', content, re.DOTALL)
        tech_matches = re.findall(r'badge/.*?-(.*?)-', content)

        if not name_match or not desc_match:
            return None

        project_name = name_match.group(1).strip()
        description = ' '.join(desc_match.group(1).strip().splitlines())
        technologies = sorted(list(set(tech for tech in tech_matches if not tech.startswith('Platform'))))

        return {"name": project_name, "description": description, "technologies": technologies}

    def _update_json_file(self, new_project_data: dict) -> Tuple[bool, Optional[str]]:
        json_path = os.path.join(API_CLONE_DIR, self.json_file_name)
        try:
            with open(json_path, 'r+', encoding='utf-8') as file:
                projects = json.load(file)
                
                if any(p['github_url'] == self.project_repo_url for p in projects):
                    return False, None
                
                max_id = max((p.get('id', 0) for p in projects), default=0)
                
                new_project_entry = {
                    "id": max_id + 1,
                    "name": new_project_data['name'],
                    "description": new_project_data['description'],
                    "technologies": new_project_data['technologies'],
                    "github_url": self.project_repo_url,
                    "live_url": ""
                }
                
                projects.append(new_project_entry)
                file.seek(0)
                json.dump(projects, file, indent=4, ensure_ascii=False)
                file.truncate()
                
                return True, new_project_data['name']

        except (FileNotFoundError, json.JSONDecodeError):
            return False, None

    def _git_commit_and_push(self, project_name: str) -> bool:
        if not self._run_command(['git', 'add', self.json_file_name], working_dir=API_CLONE_DIR):
            return False
        
        commit_message = f"feat: add '{project_name}' project to portfolio"
        if not self._run_command(['git', 'commit', '-m', commit_message], working_dir=API_CLONE_DIR):
            return False
            
        if not self._run_command(['git', 'push'], working_dir=API_CLONE_DIR):
            return False
            
        return True

    def run(self) -> None:
        with temporary_directories(API_CLONE_DIR, PROJECT_CLONE_DIR):
            if not self._clone_repo(self.api_repo_url, API_CLONE_DIR):
                raise RuntimeError("Critical failure: Could not clone the API repository.")

            if not self._clone_repo(self.project_repo_url, PROJECT_CLONE_DIR):
                raise RuntimeError("Critical failure: Could not clone the project repository.")
            
            project_data = self._parse_readme()
            if not project_data:
                raise ValueError("Failed to parse README.md. Check file format and patterns.")
            
            success, project_name = self._update_json_file(project_data)
            if not success:
                return

            if not self._git_commit_and_push(project_name):
                raise RuntimeError("Failed to push changes to the API repository.")

def setup_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Automates adding a new project to the portfolio.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument(
        "project_url",
        help="The full URL of the project repository to add."
    )
    parser.add_argument(
        "--api-url",
        default=DEFAULT_API_REPO_URL,
        help="The portfolio's API repository URL (use SSH URL for key-based auth)."
    )
    parser.add_argument(
        "--json-file",
        default=DEFAULT_JSON_FILE_NAME,
        help="The name of the JSON file to update in the API repository."
    )
    return parser.parse_args()

def main():
    args = setup_arguments()
    try:
        updater = PortfolioUpdater(
            project_url=args.project_url,
            api_url=args.api_url,
            json_file=args.json_file
        )
        updater.run()
        print("Portfolio update process completed successfully!")
    except (RuntimeError, ValueError) as e:
        print(f"An error occurred that stopped the execution: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()