# GitHub Portfolio Updater (Python)

![Language](https://img.shields.io/badge/Language-Python-blue?style=for-the-badge&logo=python)
![Type](https://img.shields.io/badge/Type-Automation_Tool-grey?style=for-the-badge&logo=powershell)
![License](https://img.shields.io/badge/License-MIT-yellow.svg?style=for-the-badge)

A command-line tool to automate portfolio updates by parsing a project's `README.md` and pushing the information to a central, Git-based API.

---



---

## 📋 Table of Contents

*   [About The Project](#-about-the-project)
*   [Key Features](#-key-features)
*   [Architecture (How It Works)](#️-architecture-how-it-works)
*   [Getting Started](#-getting-started)
    *   [Prerequisites](#prerequisites)
    *   [Installation](#installation)
*   [Usage](#️-usage)
    *   [Target README Format](#target-readme-format)

---

## 📖 About The Project

Keeping a portfolio up-to-date can be a repetitive task. For every new project, one must manually update the database or source code that feeds the portfolio website. This tool was built to eliminate that manual work.

The **GitHub Portfolio Updater** is an automation script that acts as a personal assistant. By providing the URL of one of your GitHub projects, the tool clones the repository, intelligently extracts key information from its `README.md` (like the project name, description, and technologies), and then updates, commits, and pushes this information to a separate repository that serves as the "database" for your portfolio API.

In short, it turns your `README.md` into the single source of truth for your projects, automating the entire portfolio update workflow.

---

## ✨ Key Features

*   ✅ **Automatic README Parsing**: Uses regular expressions to extract the project name, the description from the "About The Project" section, and technologies listed in Shields.io badges.
*   ✅ **Full Git Integration**: Manages the `clone`, `add`, `commit`, and `push` cycle to autonomously update the API repository.
*   ✅ **Idempotent Design**: Checks if a project already exists in the `projects.json` file before adding it, preventing duplicate entries.
*   ✅ **Command-Line Interface (CLI)**: Built with Python's `argparse` to provide a professional tool experience, with clear arguments and help messages.
*   ✅ **Safe & Automatic Cleanup**: Uses a `contextmanager` to ensure that temporary directories created during execution are always removed, even if an error occurs.
*   ✅ **Windows-Robust**: Includes an error handler to deal with `PermissionError` issues that can arise when removing `.git` files on Windows.

---

## ⚙️ Architecture (How It Works)

The tool operates in a clear, sequential workflow orchestrated by the `PortfolioUpdater` class.

1.  **Initialization (CLI)**: The script is started via the command line. `argparse` parses the user-provided arguments (the project URL and optional flags).
2.  **Temporary Environment**: A `contextmanager` creates temporary directories to clone the repositories into, ensuring the local workspace is not polluted.
3.  **Cloning**: The script clones both the **Portfolio API** repository and the target **Project** repository.
4.  **Parsing**: The `_parse_readme` method reads the `README.md` file from the target project and extracts the required data.
5.  **Updating**: The `_update_json_file` method opens the `projects.json` file from the API repository, checks for duplicates, and if none are found, appends the new entry with an incremented `id`.
6.  **Deploying**: The `_git_commit_and_push` method executes the Git commands to push the updated `projects.json` to the remote API repository.
7.  **Cleaning Up**: At the end of the run (on success or failure), the `contextmanager` automatically destroys the temporary directories.

The data flow is as follows:
**User (CLI)** → **Repo Clones** → **README Parsing** → **JSON Update** → **Git Push**

---

## 🚀 Getting Started

To run this tool on your local machine, follow the steps below.

### Prerequisites

*   **Python 3.8+**
*   **Git** installed on your system.
*   **SSH keys configured with your GitHub account**. The tool uses SSH URLs (`git@github.com:...`) to push changes without needing passwords. Follow the [official GitHub guide](https://docs.github.com/en/authentication/connecting-to-github-with-ssh/adding-a-new-ssh-key-to-your-github-account) to get set up.

### Installation

1.  Clone this repository to your machine:
    ```sh
    git clone https://github.com/your-username/github-portfolio-updater.git
    ```
2.  Navigate to the project directory:
    ```sh
    cd github-portfolio-updater
    ```
    The script is self-contained and requires no external packages to be installed.

---

## 🛠️ Usage

Run the script from your terminal, passing the URL of the project repository you wish to add as the main argument.

**Basic Command:**
```sh
python portfolio_updater.py <URL_OF_THE_PROJECT_REPOSITORY>
```
Example:
```sh
python portfolio_updater.py https://github.com/victorebouvie/js-portfolio-frontend
```
Help Command:
You can view all available options using the --help flag:
```sh
python portfolio_updater.py --help
```
Output:
```sql
usage: portfolio_updater.py [-h] [--api-url API_URL] [--json-file JSON_FILE] project_url
Automates adding a new project to the portfolio.
positional arguments:
project_url The full URL of the project repository to add.
options:
-h, --help show this help message and exit
--api-url API_URL The portfolio's API repository URL (use SSH URL for key-based auth). (default: git@github.com:victorebouvie/python-portfolio-api.git)
--json-file JSON_FILE
The name of the JSON file to update in the API repository. (default: projects.json)
```

### Target README Format

For the parser to work correctly, your project's `README.md` **must** follow a minimal structure:

1.  **The project title** must be the first H1 header in the file.
    ```markdown
    # My Awesome Project Name
    ```

2.  **The project description** must be under an H2 header named "About The Project", which may optionally contain the 📖 emoji. The script captures all text between this header and the next horizontal rule (`---`).
    ```markdown
    ## 📖 About The Project

    This is the detailed description of my project. This entire paragraph will be captured and used as the portfolio description.

    ---
    ```

3.  **Technologies** are extracted from [Shields.io](https://shields.io/) badge URLs by looking for the pattern `badge/...-TECHNOLOGY_NAME-...`.
    ```markdown
    ![JavaScript](https://img.shields.io/badge/Language-JavaScript-yellow?style=for-the-badge&logo=javascript)
    ```
