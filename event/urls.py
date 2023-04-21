from django.urls import path
from .views import adminViews,endUserViews,eventViews,qrCodeViews,reportViews


urlpatterns = [

    path('admin',eventViews.EventListView.as_view(),name='admin-dash'),
    path('event/create',eventViews.EventCreateView.as_view(),name='event-create'),
    path(r'event/<int:pk>',eventViews.EventDetailView.as_view(),name='event-detail'),
    path(r'event/<int:pk>/update',eventViews.EventUpdateView.as_view(),name='event-update'),
    path(r'event/<int:pk>/delete',eventViews.EventDeleteView.as_view(),name='event-delete'),
    path(r'event/<int:pk>/publish',eventViews.PublishEventView.as_view(),name='event-publish'),
    path(r'event/<int:pk>/unpublish',eventViews.UnPublishEventView.as_view(),name='event-unpublish'),
    path('event/<int:pk>/register',eventViews.EventRegistrationView.as_view(),name='event-register'),
    path('event/history',eventViews.EventHistoryListView.as_view(),name='event-history'),

    path('admin/published_events',adminViews.PublishedEventListView.as_view(),name='published_event'),

    path('home',endUserViews.EndUserPublishedEventListView.as_view(),name='user-dash'),
    path('home/registeredevents',endUserViews.RegisteredEventsListView.as_view(),name='registered-events'),
    path('home/attended',endUserViews.EventsHistoryView.as_view(),name='attended-events'),
    path(r'home/attended/<int:pk>/certificate',endUserViews.GenerateCertificateView.as_view(),name='generate-cert'),

    path('generate/<int:user>/<int:event>/',qrCodeViews.test,name="generate_qr_code"),
    # path('scan',qrCodeViews.test2,name="test2"),
    # path('validate',qrCodeViews.scan_qr_code,name="scan_qr_code"),

    path('admin/report/semester',reportViews.GenerateSemesterBasedReportView.as_view(),name='semester-report'),
    path('admin/report/organizer',reportViews.GenerateOrganizerBasedReportView.as_view(),name='organizer-report'),
    path(r'admin/report/event/<int:pk>',reportViews.GenerateEventBasedReport.as_view(),name='event-report'),
    path('admin/report',reportViews.GenerateReportView.as_view(),name='report'),


]