from django.urls import path
from .views import adminViews,endUserViews,eventViews


urlpatterns = [

    path('admin',eventViews.EventListView.as_view(),name='admin-dash'),
    path('event/create',eventViews.EventCreateView.as_view(),name='event-create'),
    path(r'event/<int:pk>',eventViews.EventDetailView.as_view(),name='event-detail'),
    path(r'event/<int:pk>/update',eventViews.EventUpdateView.as_view(),name='event-update'),
    path(r'event/<int:pk>/delete',eventViews.EventDeleteView.as_view(),name='event-delete'),
    path(r'event/<int:pk>/publish',eventViews.PublishEventView.as_view(),name='event-publish'),
    path(r'event/<int:pk>/unpublish',eventViews.UnPublishEventView.as_view(),name='event-unpublish'),

    path('admin/published_events',adminViews.PublishedEventListView.as_view(),name='published_event'),

    path('home',endUserViews.EndUUserPublishedEventListView.as_view(),name='user-dash'),

]