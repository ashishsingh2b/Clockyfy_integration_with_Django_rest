from django.urls import path
from .views import (
    WorkspaceView, CreateProjectView, StartTimerView, StopTimerView,
    CreateTaskView, StartTaskTimerView, StopTaskTimerView, GetProjectTasksView,UserTimeReportView, ProjectTimeReportView, TaskAssignmentView,
    TimerStatusView, BulkTaskCreateView
)

urlpatterns = [
    path('workspaces/', WorkspaceView.as_view(), name='workspaces'),
    path('projects/create/', CreateProjectView.as_view(), name='create-project'),
    path('timer/start/', StartTimerView.as_view(), name='start-timer'),
    path('timer/stop/', StopTimerView.as_view(), name='stop-timer'),
    path('tasks/create/', CreateTaskView.as_view(), name='create-task'),
    path('tasks/start-timer/', StartTaskTimerView.as_view(), name='start-task-timer'),
    path('tasks/stop-timer/', StopTaskTimerView.as_view(), name='stop-task-timer'),
    path('workspaces/<str:workspace_id>/projects/<str:project_id>/tasks/', 
         GetProjectTasksView.as_view(), name='get-project-tasks'),
    path('users/<str:user_id>/time-report/',UserTimeReportView.as_view(),name='user-time-report'),
    path('projects/<str:project_id>/time-report/',ProjectTimeReportView.as_view(),name='project-time-report'),
    path('tasks/<str:task_id>/assign/',TaskAssignmentView.as_view(),name='assign-task'),
    path('timer/status/', TimerStatusView.as_view(),name='timer-status'),
    path('tasks/bulk-create/', BulkTaskCreateView.as_view(),name='bulk-create-tasks'),
]












# from django.urls import path
# from .views import WorkspaceView, CreateProjectView, StartTimerView, StopTimerView

# urlpatterns = [
#     path('workspaces/', WorkspaceView.as_view(), name='workspaces'),
#     path('workspaces/projects/', CreateProjectView.as_view(), name='create_project'),
#     path('workspaces/start-timer/', StartTimerView.as_view(), name='start_timer'),
#     path('workspaces/stop-timer/', StopTimerView.as_view(), name='stop-timer'),

# ]

