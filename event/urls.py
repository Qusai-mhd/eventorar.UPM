from django.urls import path
from .views import adminViews,endUserViews,eventViews

urlpatterns = [
    path('event',eventViews.EventListView.as_view(),name='created-events-list'),
    path('event/create',eventViews.EventCreateView.as_view(),name='event-create'),
    path(r'event/<int:pk>',eventViews.EventDetailView.as_view(),name='event-detail'),
    path(r'event/<int:pk>/update',eventViews.EventUpdateView.as_view(),name='event-update'),
    path(r'event/<int:pk>/delete',eventViews.EventDeleteView.as_view(),name='event-delete'),

]