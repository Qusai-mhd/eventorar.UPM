from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.views.generic import ListView
from ..models import PublishedEvent
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.utils import timezone


@method_decorator(login_required,name="dispatch")
class EndUUserPublishedEventListView(ListView):
    model=PublishedEvent
    template_name='endUserTemplates/enduserdash.html'
    context_object_name='events'
    paginate_by=5

    def get_context_data(self, **kwargs):
        context = super(EndUUserPublishedEventListView, self).get_context_data(**kwargs)
        events = self.get_queryset()
        page = self.request.GET.get('page')
        paginator = Paginator(events, self.paginate_by)
        try:
            events = paginator.page(page)
        except PageNotAnInteger:
            events = paginator.page(1)
        except EmptyPage:
            events = paginator.page(paginator.num_pages)
        context['events'] = events
        return context
    
    def get_queryset(self):
        today=timezone.now().date()
        user=self.request.user
        group_ids=user.groups.values_list('id',flat=True)
        return PublishedEvent.objects.filter(
            Q(target_audience__id__in=group_ids) &
            Q(event__date__gte=today))
            