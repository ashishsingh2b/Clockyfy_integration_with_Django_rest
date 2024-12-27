# clockify.py
import requests
from django.conf import settings
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import logging

logger = logging.getLogger(__name__)



class ClockifyService:
    def __init__(self):
        self.api_key = settings.CLOCKIFY_API_KEY
        self.base_url = settings.CLOCKIFY_BASE_URL
        self.headers = {
            "X-Api-Key": self.api_key,
            "Content-Type": "application/json"
        }

    ########### New Feature Auth #################


        
    def validate_ids(self, workspace_id: str, project_id: Optional[str] = None, 
                    task_id: Optional[str] = None) -> bool:
        """Validate that the provided IDs exist in Clockify"""
        try:
            # Validate workspace
            self.get_workspace_by_id(workspace_id)
            
            # Validate project if provided
            if project_id:
                self.get_project_by_id(workspace_id, project_id)
                
            # Validate task if provided
            if task_id:
                self.get_task_by_id(workspace_id, project_id, task_id)
                
            return True
        except requests.exceptions.RequestException:
            return False

    def get_user_time_report(self, workspace_id: str, user_id: str, 
                           start_date: datetime, end_date: datetime) -> Dict:
        """Get time tracking report for a specific user"""
        url = f"{self.base_url}/workspaces/{workspace_id}/reports/detailed"
        
        payload = {
            "dateRangeStart": start_date.isoformat(),
            "dateRangeEnd": end_date.isoformat(),
            "users": {"ids": [user_id]},
            "detailedFilter": {
                "page": 1,
                "pageSize": 50
            }
        }
        
        response = requests.post(url, json=payload, headers=self.headers)
        response.raise_for_status()
        return response.json()

    def get_project_time_report(self, workspace_id: str, project_id: str) -> Dict:
        """Get time tracking report for a specific project"""
        url = f"{self.base_url}/workspaces/{workspace_id}/projects/{project_id}/reports/summary"
        response = requests.get(url, headers=self.headers)
        response.raise_for_status()
        return response.json()

    def assign_task(self, workspace_id: str, project_id: str, 
                   task_id: str, user_ids: List[str]) -> Dict:
        """Assign a task to specific users"""
        url = f"{self.base_url}/workspaces/{workspace_id}/projects/{project_id}/tasks/{task_id}"
        
        payload = {
            "assigneeIds": user_ids
        }
        
        response = requests.put(url, json=payload, headers=self.headers)
        response.raise_for_status()
        return response.json()

    def get_timer_status(self, workspace_id: str, user_id: str) -> Dict:
        """Get the current timer status for a user"""
        url = f"{self.base_url}/workspaces/{workspace_id}/user/{user_id}/time-entries"
        params = {
            "in-progress": "true"
        }
        
        response = requests.get(url, headers=self.headers, params=params)
        response.raise_for_status()
        return response.json()

    def bulk_create_tasks(self, workspace_id: str, project_id: str, 
                         tasks: List[Dict]) -> List[Dict]:
        """Bulk create tasks in a project"""
        created_tasks = []
        
        for task in tasks:
            try:
                created_task = self.create_task(
                    workspace_id, 
                    project_id, 
                    task['name'], 
                    task.get('assignee_ids', [])
                )
                created_tasks.append(created_task)
            except Exception as e:
                logger.error(f"Error creating task {task['name']}: {str(e)}")
                
        return created_tasks

    def add_tags_to_task(self, workspace_id: str, project_id: str, 
                        task_id: str, tags: List[str]) -> Dict:
        """Add tags to a task"""
        url = f"{self.base_url}/workspaces/{workspace_id}/projects/{project_id}/tasks/{task_id}"
        
        payload = {
            "tags": tags
        }
        
        response = requests.put(url, json=payload, headers=self.headers)
        response.raise_for_status()
        return response.json()   


    ############# Till Task Implementations ###############


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
    

    