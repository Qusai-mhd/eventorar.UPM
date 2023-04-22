from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.mixins import UserPassesTestMixin
from django.contrib.auth.decorators import user_passes_test
from django.views.generic import ListView
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from ..models import PublishedEvent

class PublishedEventListView(UserPassesTestMixin,ListView):
    model=PublishedEvent
    template_name='adminTemplates/published_events.html'
    queryset=PublishedEvent.objects.filter(is_held=False)
    context_object_name='events'
    paginate_by=5
    def get_context_data(self, **kwargs):
        context = super(PublishedEventListView, self).get_context_data(**kwargs)
        published_events = self.get_queryset()
        page = self.request.GET.get('page')
        paginator = Paginator(published_events, self.paginate_by)
        try:
            published_events = paginator.page(page)
        except PageNotAnInteger:
            published_events = paginator.page(1)
        except EmptyPage:
            published_events = paginator.page(paginator.num_pages)
        context['events'] = published_events
        return context
    def test_func(self):
        return self.request.user.is_superuser
