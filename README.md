# GitLab Branch Protector

GitLab Branch Protector is a Python utility that automates the management of branch protection settings across multiple GitLab projects.

## Features

- **Automated Project Retrieval:**
  Fetches all projects from one or more GitLab groups using the GitLab API with support for pagination.

- **Branch Protection Management:**
  Checks if a branch is protected and, if necessary, removes and re-applies protection settings to update permissions.

- **Configurable Protection Settings:**
  Enforces branch protection by allowing only users with Developer access (or higher) to push and merge, while disallowing force pushes.

- **Environment-Based Configuration:**
  All sensitive data (GitLab URL, tokens, group names, etc.) are provided via environment variables, making the tool secure and adaptable.

```bash
pip install requests
