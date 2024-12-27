from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .services.clockify_service import ClockifyService
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth.models import User
from datetime import datetime, timedelta
import requests
import logging

logger = logging.getLogger(__name__)

class BaseClockifyView(APIView):
    permission_classes = [IsAuthenticated]
    
    def __init__(self):
        super().__init__()
        self.service = ClockifyService()

    def validate_ids(self, workspace_id, project_id=None, task_id=None):
        if not self.service.validate_ids(workspace_id, project_id, task_id):
            raise ValueError("Invalid ID(s) provided")

class UserTimeReportView(BaseClockifyView):
    def get(self, request, user_id):
        try:
            workspace_id = request.query_params.get('workspace_id')
            if not workspace_id:
                return Response(
                    {"error": "workspace_id is required"}, 
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Default to last 30 days if dates not provided
            end_date = datetime.now()
            start_date = end_date - timedelta(days=30)
            
            report = self.service.get_user_time_report(
                workspace_id, user_id, start_date, end_date
            )
            
            return Response(report, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Error fetching user time report: {str(e)}")
            return Response(
                {"error": str(e)}, 
                status=status.HTTP_400_BAD_REQUEST
            )

class ProjectTimeReportView(BaseClockifyView):
    def get(self, request, project_id):
        try:
            workspace_id = request.query_params.get('workspace_id')
            if not workspace_id:
                return Response(
                    {"error": "workspace_id is required"}, 
                    status=status.HTTP_400_BAD_REQUEST
                )

            self.validate_ids(workspace_id, project_id)
            
            report = self.service.get_project_time_report(workspace_id, project_id)
            return Response(report, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Error fetching project time report: {str(e)}")
            return Response(
                {"error": str(e)}, 
                status=status.HTTP_400_BAD_REQUEST
            )

class TaskAssignmentView(BaseClockifyView):
    def post(self, request, task_id):
        try:
            workspace_id = request.data.get('workspace_id')
            project_id = request.data.get('project_id')
            user_ids = request.data.get('user_ids', [])

            if not all([workspace_id, project_id]):
                return Response(
                    {"error": "workspace_id and project_id are required"}, 
                    status=status.HTTP_400_BAD_REQUEST
                )

            self.validate_ids(workspace_id, project_id, task_id)
            
            result = self.service.assign_task(
                workspace_id, project_id, task_id, user_ids
            )
            return Response(result, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Error assigning task: {str(e)}")
            return Response(
                {"error": str(e)}, 
                status=status.HTTP_400_BAD_REQUEST
            )

class TimerStatusView(BaseClockifyView):
    def get(self, request):
        try:
            workspace_id = request.query_params.get('workspace_id')
            user_id = request.user.id  # Assuming user is authenticated

            if not workspace_id:
                return Response(
                    {"error": "workspace_id is required"}, 
                    status=status.HTTP_400_BAD_REQUEST
                )

            status = self.service.get_timer_status(workspace_id, user_id)
            return Response(status, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Error fetching timer status: {str(e)}")
            return Response(
                {"error": str(e)}, 
                status=status.HTTP_400_BAD_REQUEST
            )

class BulkTaskCreateView(BaseClockifyView):
    def post(self, request):
        try:
            workspace_id = request.data.get('workspace_id')
            project_id = request.data.get('project_id')
            tasks = request.data.get('tasks', [])

            if not all([workspace_id, project_id, tasks]):
                return Response(
                    {"error": "workspace_id, project_id, and tasks are required"}, 
                    status=status.HTTP_400_BAD_REQUEST
                )

            self.validate_ids(workspace_id, project_id)
            
            created_tasks = self.service.bulk_create_tasks(
                workspace_id, project_id, tasks
            )
            return Response(created_tasks, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            logger.error(f"Error creating tasks in bulk: {str(e)}")
            return Response(
                {"error": str(e)}, 
                status=status.HTTP_400_BAD_REQUEST
            )


############ Old Features ##################
class WorkspaceView(APIView):
    def get(self, request):
        try:
            service = ClockifyService()
            print(f"==>> service: {service}")
            workspaces = service.get_workspaces()
            print(f"==>> workspaces: {workspaces}")
            return Response(workspaces, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f"Error fetching workspaces: {e}")
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

class CreateProjectView(APIView):
    def post(self, request):
        workspace_id = request.data.get("workspace_id")

        try:
            service = ClockifyService()
            project_name = request.data.get("name")

            if not project_name:
                return Response({"error": "Project name is required"}, status=status.HTTP_400_BAD_REQUEST)

            project = service.create_project(workspace_id, project_name)
            return Response(project, status=status.HTTP_201_CREATED)
        
        except Exception as e:
            logger.error(f"Error creating project: {e}")
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

class StartTimerView(APIView):
    def post(self, request):
        workspace_id = request.data.get("workspace_id")
        project_id = request.data.get("project_id")
        description = request.data.get("description", "")

        if not workspace_id or not project_id:
            return Response({"error": "Workspace ID and Project ID are required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            service = ClockifyService()
            time_entry = service.start_timer(workspace_id, project_id, description)
            return Response(time_entry, status=status.HTTP_201_CREATED)
        
        except Exception as e:
            logger.error(f"Error starting timer: {e}")
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

class StopTimerView(APIView):
    def put(self, request):
        workspace_id = request.data.get("workspaceId")
        time_entry_id = request.data.get("timeEntryId")
        
        print(f"Received request data: {request.data}")
        
        if not workspace_id or not time_entry_id:
            return Response(
                {"error": "workspaceId and timeEntryId are required"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        service = ClockifyService()
        try:
            response = service.stop_timer(workspace_id, time_entry_id)
            return Response(response, status=status.HTTP_200_OK)
        except requests.exceptions.RequestException as e:
            error_message = f"Error stopping timer: {str(e)}"
            if hasattr(e, 'response') and e.response is not None:
                error_message += f"\nResponse content: {e.response.text}"
            logger.error(error_message)
            return Response(
                {"error": error_message}, 
                status=status.HTTP_400_BAD_REQUEST
            )

class CreateTaskView(APIView):
    def post(self, request):
        workspace_id = request.data.get("workspace_id")
        project_id = request.data.get("project_id")
        task_name = request.data.get("name")
        assignee_ids = request.data.get("assignee_ids", [])

        if not all([workspace_id, project_id, task_name]):
            return Response(
                {"error": "workspace_id, project_id, and name are required"}, 
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            service = ClockifyService()
            task = service.create_task(workspace_id, project_id, task_name, assignee_ids)
            return Response(task, status=status.HTTP_201_CREATED)
        except Exception as e:
            logger.error(f"Error creating task: {e}")
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

class StartTaskTimerView(APIView):
    def post(self, request):
        workspace_id = request.data.get("workspace_id")
        project_id = request.data.get("project_id")
        task_id = request.data.get("task_id")
        description = request.data.get("description", "")

        if not all([workspace_id, project_id, task_id]):
            return Response(
                {"error": "workspace_id, project_id, and task_id are required"}, 
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            service = ClockifyService()
            time_entry = service.start_task_timer(
                workspace_id, project_id, task_id, description
            )
            return Response({
                "message": "Timer started successfully",
                "time_entry": time_entry
            }, status=status.HTTP_201_CREATED)
        except Exception as e:
            logger.error(f"Error starting task timer: {e}")
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

class StopTaskTimerView(APIView):
    def put(self, request):
        workspace_id = request.data.get("workspace_id")
        time_entry_id = request.data.get("time_entry_id")
        
        print(f"Received request data: {request.data}")
        
        if not workspace_id or not time_entry_id:
            return Response(
                {"error": "workspace_id and time_entry_id are required"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        service = ClockifyService()
        try:
            response = service.stop_task_timer(workspace_id, time_entry_id)
            return Response({
                "message": "Timer stopped successfully",
                "time_entry": response
            }, status=status.HTTP_200_OK)
        except requests.exceptions.RequestException as e:
            error_message = f"Error stopping task timer: {str(e)}"
            if hasattr(e, 'response') and e.response is not None:
                error_message += f"\nResponse content: {e.response.text}"
            logger.error(error_message)
            return Response(
                {"error": error_message}, 
                status=status.HTTP_400_BAD_REQUEST
            )

class GetProjectTasksView(APIView):
    def get(self, request, workspace_id, project_id):
        try:
            service = ClockifyService()
            tasks = service.get_project_tasks(workspace_id, project_id)
            return Response(tasks, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f"Error fetching tasks: {e}")
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)














# from rest_framework.views import APIView
# from rest_framework.response import Response
# from rest_framework import status
# from .services.clockify_service import ClockifyService
# import requests
# import logging

# # Setup logger
# logger = logging.getLogger(__name__)

# class WorkspaceView(APIView):
#     def get(self, request):
#         try:
#             service = ClockifyService()
#             print(f"==>> service: {service}")
#             workspaces = service.get_workspaces()
#             print(f"==>> workspaces: {workspaces}")
#             return Response(workspaces, status=status.HTTP_200_OK)
#         except Exception as e:
#             logger.error(f"Error fetching workspaces: {e}")
#             return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

# class CreateProjectView(APIView):
#     def post(self, request):
#         # Hardcoded Workspace ID
#         workspace_id = "676bf4dc9124eb4caeffd66e"  # Your Workspace ID

#         try:
#             service = ClockifyService()

#             # Get the project name from the request body
#             project_name = request.data.get("name")

#             # Validate the project name
#             if not project_name:
#                 return Response({"error": "Project name is required"}, status=status.HTTP_400_BAD_REQUEST)

#             # Create the project in Clockify
#             project = service.create_project(workspace_id, project_name)

#             return Response(project, status=status.HTTP_201_CREATED)
        
#         except Exception as e:
#             logger.error(f"Error creating project: {e}")
#             return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

# class StartTimerView(APIView):
#     def post(self, request):
#         workspace_id = request.data.get("workspace_id")
#         project_id = request.data.get("project_id")
#         description = request.data.get("description", "")  # Optional

#         if not workspace_id or not project_id:
#             return Response({"error": "Workspace ID and Project ID are required"}, status=status.HTTP_400_BAD_REQUEST)

#         try:
#             service = ClockifyService()

#             # Start the timer
#             time_entry = service.start_timer(workspace_id, project_id, description)

#             return Response(time_entry, status=status.HTTP_201_CREATED)
        
#         except Exception as e:
#             logger.error(f"Error starting timer: {e}")
#             return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

# class StopTimerView(APIView):
#     def put(self, request):  # Changed from patch to put
#         workspace_id = request.data.get("workspaceId")
#         time_entry_id = request.data.get("timeEntryId")
        
#         print(f"Received request data: {request.data}")
        
#         if not workspace_id or not time_entry_id:
#             return Response(
#                 {"error": "workspaceId and timeEntryId are required"}, 
#                 status=status.HTTP_400_BAD_REQUEST
#             )
        
#         service = ClockifyService()
#         try:
#             response = service.stop_timer(workspace_id, time_entry_id)
#             return Response(response, status=status.HTTP_200_OK)
#         except requests.exceptions.RequestException as e:
#             error_message = f"Error stopping timer: {str(e)}"
#             if hasattr(e, 'response') and e.response is not None:
#                 error_message += f"\nResponse content: {e.response.text}"
#             logger.error(error_message)
#             return Response(
#                 {"error": error_message}, 
#                 status=status.HTTP_400_BAD_REQUEST
#             )
        
        