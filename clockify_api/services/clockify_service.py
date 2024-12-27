# clockify.py
import requests
from django.conf import settings
from datetime import datetime

class ClockifyService:
    def __init__(self):
        self.api_key = settings.CLOCKIFY_API_KEY
        self.base_url = settings.CLOCKIFY_BASE_URL
        self.headers = {
            "X-Api-Key": self.api_key,
            "Content-Type": "application/json"
        }

    def get_workspaces(self):
        url = f"{self.base_url}/workspaces"
        response = requests.get(url, headers=self.headers)
        response.raise_for_status()
        return response.json()

    def create_project(self, workspace_id, project_name):
        url = f"{self.base_url}/workspaces/{workspace_id}/projects"
        payload = {"name": project_name}
        response = requests.post(url, json=payload, headers=self.headers)
        response.raise_for_status()
        return response.json()

    def start_timer(self, workspace_id, project_id, description=""):
        url = f"{self.base_url}/workspaces/{workspace_id}/time-entries"
        payload = {
            "start": datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ"),
            "billable": True,
            "projectId": project_id,
            "description": description
        }
        response = requests.post(url, json=payload, headers=self.headers)
        response.raise_for_status()
        return response.json()

    def stop_timer(self, workspace_id, time_entry_id):
        get_url = f"{self.base_url}/workspaces/{workspace_id}/time-entries/{time_entry_id}"
        existing_entry = requests.get(get_url, headers=self.headers).json()
        
        data = {
            "start": existing_entry['timeInterval']['start'],
            "end": datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ"),
            "billable": existing_entry['billable'],
            "projectId": existing_entry['projectId']
        }
        
        response = requests.put(get_url, headers=self.headers, json=data)
        
        if response.status_code != 200:
            print(f"Response Content: {response.text}")
            print(f"Response Status: {response.status_code}")
        
        response.raise_for_status()
        return response.json()

    def create_task(self, workspace_id, project_id, task_name, assignee_ids=None):
        url = f"{self.base_url}/workspaces/{workspace_id}/projects/{project_id}/tasks"
        payload = {
            "name": task_name,
            "projectId": project_id,
            "assigneeIds": assignee_ids or [],
            "status": "ACTIVE"
        }
        response = requests.post(url, json=payload, headers=self.headers)
        response.raise_for_status()
        return response.json()

    def start_task_timer(self, workspace_id, project_id, task_id, description=""):
        url = f"{self.base_url}/workspaces/{workspace_id}/time-entries"
        current_time = datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ")
        
        payload = {
            "start": current_time,
            "billable": True,
            "projectId": project_id,
            "taskId": task_id,
            "description": description
        }
        
        print(f"Starting timer with payload: {payload}")
        response = requests.post(url, json=payload, headers=self.headers)
        
        if response.status_code != 200 and response.status_code != 201:
            print(f"Response Content: {response.text}")
            print(f"Response Status: {response.status_code}")
            
        response.raise_for_status()
        return response.json()

    def stop_task_timer(self, workspace_id, time_entry_id):
        get_url = f"{self.base_url}/workspaces/{workspace_id}/time-entries/{time_entry_id}"
        existing_entry = requests.get(get_url, headers=self.headers).json()
        
        data = {
            "start": existing_entry['timeInterval']['start'],
            "end": datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ"),
            "billable": existing_entry['billable'],
            "projectId": existing_entry['projectId'],
            "taskId": existing_entry['taskId']
        }
        
        response = requests.put(get_url, headers=self.headers, json=data)
        
        if response.status_code != 200:
            print(f"Response Content: {response.text}")
            print(f"Response Status: {response.status_code}")
        
        response.raise_for_status()
        return response.json()

    def get_project_tasks(self, workspace_id, project_id):
        url = f"{self.base_url}/workspaces/{workspace_id}/projects/{project_id}/tasks"
        response = requests.get(url, headers=self.headers)
        response.raise_for_status()
        return response.json()




















# import requests
# from django.conf import settings
# from datetime import datetime

# class ClockifyService:
#     def __init__(self):
#         # Load the API key and base URL from Django settings
#         self.api_key = settings.CLOCKIFY_API_KEY
#         self.base_url = settings.CLOCKIFY_BASE_URL
#         self.headers = {
#             "X-Api-Key": self.api_key,
#             "Content-Type": "application/json"
#         }

#     # Get all workspaces
#     def get_workspaces(self):
#         url = f"{self.base_url}/workspaces"
#         response = requests.get(url, headers=self.headers)
#         response.raise_for_status()  # To raise an exception if the request fails
#         return response.json()

#     # Create a project in a specific workspace
#     def create_project(self, workspace_id, project_name):
#         url = f"{self.base_url}/workspaces/{workspace_id}/projects"
#         payload = {"name": project_name}
#         response = requests.post(url, json=payload, headers=self.headers)
#         response.raise_for_status()  # To raise an exception if the request fails
#         return response.json()

#     # Start a timer (create a time entry)
#     def start_timer(self, workspace_id, project_id, description=""):
#         url = f"{self.base_url}/workspaces/{workspace_id}/time-entries"
#         payload = {
#             "start": "2024-12-26T08:00:00Z",  # Replace with current time as needed
#             "billable": True,
#             "projectId": project_id,
#             "description": description
#         }
#         response = requests.post(url, json=payload, headers=self.headers)
#         response.raise_for_status()  # To raise an exception if the request fails
#         return response.json()

#     # Stop a timer (end the time entry)

#     def stop_timer(self, workspace_id, time_entry_id):
#         # First get the existing time entry details
#         get_url = f"{self.base_url}/workspaces/{workspace_id}/time-entries/{time_entry_id}"
#         existing_entry = requests.get(get_url, headers=self.headers).json()
        
#         # Now update with the end time
#         data = {
#             "start": existing_entry['timeInterval']['start'],
#             "end": datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ"),
#             "billable": existing_entry['billable'],
#             "projectId": existing_entry['projectId']
#         }
        
#         response = requests.put(get_url, headers=self.headers, json=data)
        
#         if response.status_code != 200:
#             print(f"Response Content: {response.text}")
#             print(f"Response Status: {response.status_code}")
        
#         response.raise_for_status()
#         return response.json()
    

    