from django.urls import reverse_lazy
from django.views.generic import ListView,CreateView,DetailView,DeleteView,UpdateView
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from ..models import Event

class EventListView(ListView):
    model=Event
    template_name='eventTemplates/crud/eventList.html'
    context_object_name='events'
    paginate_by=5
    def get_context_data(self, **kwargs):
        context = super(EventListView, self).get_context_data(**kwargs)
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
    
class EventCreateView(CreateView):
    model=Event
    template_name='eventTemplates/crud/createEvent.html'
    fields='name','organizer','date','time','location','description'
    
    def get_success_url(self):
        return reverse_lazy('event-detail',kwargs={'pk':self.object.id})

class EventDetailView(DetailView):
    model=Event
    template_name='eventTemplates/crud/detail.html'
    context_object_name='event'

class EventUpdateView(UpdateView):
    model=Event
    template_name='eventTemplates/crud/update.html'
    context_object_name='event'
    fields='name','organizer','date','time','location','description'
    
    def get_success_url(self):
        return reverse_lazy('event-detail',kwargs={'pk': self.object.id})


class EventDeleteView(DeleteView):
    model=Event
    template_name='eventTemplates/crud/delete.html'
    context_object_name='event'
    success_url=reverse_lazy('created-events-list')
