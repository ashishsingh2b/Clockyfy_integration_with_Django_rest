from django.urls import path
from .views import WorkspaceView, CreateProjectView, StartTimerView, StopTimerView

urlpatterns = [
    path('workspaces/', WorkspaceView.as_view(), name='workspaces'),
    path('workspaces/projects/', CreateProjectView.as_view(), name='create_project'),
    path('workspaces/start-timer/', StartTimerView.as_view(), name='start_timer'),
    path('workspaces/stop-timer/', StopTimerView.as_view(), name='stop-timer'),

]



# from django.urls import path
# from .views import WorkspaceView, CreateProjectView

# urlpatterns = [
#     path('workspaces/', WorkspaceView.as_view(), name='workspaces'),
#     path('workspaces/<str:workspace_id>/projects/', CreateProjectView.as_view(), name='create_project'),
# ]
