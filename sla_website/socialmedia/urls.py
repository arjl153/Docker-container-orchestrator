from django.urls import path
from . import views


app_name = 'socialmedia'

    
urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
	#homepage

    #path('<pk>/', views.DetailView.as_view(), name = 'detail'),

    #path('post/add/', views.PostCreate.as_view(), name = 'add-post'),
    path('api/v1/_count', views.CountRequests.as_view(), name = 'count-requests'),
    path('api/v1/categories', views.ListAddActsCategories.as_view(), name = 'list-add-acts'),
    path('api/v1/categories/<actType>', views.DeleteActsCategories.as_view(), name = 'delete-acts'),
    path('api/v1/categories/<actType>/acts', views.ListPostAct.as_view(), name = 'list-posts-for-act'),
    path('api/v1/categories/<actType>/acts/size', views.ListPostsSize.as_view(), name = 'list-posts-size'),

    path('api/v1/acts/count', views.CountTotalActs.as_view(), name = 'count-total-acts'),
    path('api/v1/acts/upvote', views.UpvotePost.as_view(), name = 'upvote-post'),

	path('api/v1/acts/<actID>', views.RemovePost.as_view(), name = 'delete-post'),

    path('api/v1/acts', views.AddPost.as_view(), name = 'upload-post'),    

	# Project
    path('api/v1/_health', views.HealthCheck.as_view(), name = 'health-check'),
    path('api/v1/_crash', views.CrashContainer.as_view(), name = 'crash-container'),

]	
