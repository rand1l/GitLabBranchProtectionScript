import requests
import os

# Get configuration values from environment variables
GITLAB_URL = os.getenv('GITLAB_URL')
if not GITLAB_URL:
    raise EnvironmentError("GITLAB_URL environment variable is not set.")

GITLAB_TOKEN = os.getenv('GITLAB_TOKEN')
if not GITLAB_TOKEN:
    raise EnvironmentError("GITLAB_TOKEN environment variable is not set.")

GROUPS = os.getenv('GROUPS')
if not GROUPS:
    raise EnvironmentError("GROUPS environment variable is not set.")
GROUPS = GROUPS.split(',')

PROTECTED_BRANCHES = os.getenv('PROTECTED_BRANCHES')
if not PROTECTED_BRANCHES:
    raise EnvironmentError("PROTECTED_BRANCHES environment variable is not set.")
PROTECTED_BRANCHES = PROTECTED_BRANCHES.split(',')

DEVELOPER_ACCESS = 30  # Developer access level

HEADERS = {
    'Private-Token': GITLAB_TOKEN
}


def get_projects(group_name):
    """Fetch all projects for a group with pagination."""
    group_id_url = f'{GITLAB_URL}/api/v4/groups/{group_name}'
    response = requests.get(group_id_url, headers=HEADERS)
    response.raise_for_status()
    group_id = response.json()['id']

    projects = []
    page = 1
    while True:
        projects_url = f'{GITLAB_URL}/api/v4/groups/{group_id}/projects?page={page}&per_page=100'
        response = requests.get(projects_url, headers=HEADERS)
        response.raise_for_status()

        current_projects = response.json()
        if not current_projects:
            break

        projects.extend(current_projects)
        page += 1

    print(f'Found {len(projects)} projects in group {group_name}.')
    return projects


def get_protected_branches(project_id):
    """Fetch the list of protected branches for a project."""
    protected_branches_url = f'{GITLAB_URL}/api/v4/projects/{project_id}/protected_branches'
    response = requests.get(protected_branches_url, headers=HEADERS)
    response.raise_for_status()
    return response.json()


def protect_branch(project_id, project_name, branch_name):
    """Update branch protection settings for a given branch."""
    protected_branches = get_protected_branches(project_id)
    branch_protected = any(branch['name'] == branch_name for branch in protected_branches)

    if branch_protected:
        print(f'Updating protection for branch {branch_name} in project {project_name} (ID: {project_id})...')
        # Remove current protection to update settings
        delete_url = f'{GITLAB_URL}/api/v4/projects/{project_id}/protected_branches/{branch_name}'
        requests.delete(delete_url, headers=HEADERS)

    protect_url = f'{GITLAB_URL}/api/v4/projects/{project_id}/protected_branches'
    data = {
        'name': branch_name,
        'push_access_level': DEVELOPER_ACCESS,  # Allow push for Developer and above
        'merge_access_level': DEVELOPER_ACCESS,  # Allow merge for Developer and above
        'allow_force_push': False  # Disable force push
    }

    response = requests.post(protect_url, headers=HEADERS, json=data)
    if response.status_code == 201:
        print(f'Branch {branch_name} in project {project_name} (ID: {project_id}) is now protected.')
    elif response.status_code == 400:
        print(f'Branch {branch_name} in project {project_name} (ID: {project_id}) is already protected. Updating settings.')
        update_url = f'{GITLAB_URL}/api/v4/projects/{project_id}/protected_branches/{branch_name}'
        response = requests.put(update_url, headers=HEADERS, json=data)
        if response.status_code == 200:
            print(f'Updated protection settings for branch {branch_name} in project {project_name} (ID: {project_id}).')
        else:
            print(f'Failed to update settings for branch {branch_name} in project {project_name} (ID: {project_id}). Status: {response.status_code}')
    else:
        print(f'Failed to protect branch {branch_name} in project {project_name} (ID: {project_id}). Status: {response.status_code}')


def main():
    for group in GROUPS:
        print(f'Processing group: {group}...')
        projects = get_projects(group)
        for project in projects:
            project_id = project['id']
            project_name = project['name']
            for branch in PROTECTED_BRANCHES:
                protect_branch(project_id, project_name, branch)


if __name__ == '__main__':
    main()
