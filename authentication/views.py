from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import LoginForm


login_required(login_url='auth:login')
def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data.get('email')
            password = form.cleaned_data.get('password')

        user = authenticate(request, username=email, password=password)

        if user is not None:
            login(request, user)
            if user.is_superuser:
                return redirect('event:created-events-list')
            else:
                return redirect('event:home')

        else:
            messages.error(request, 'Invalid email or password.')
            return redirect('auth:login')
    else:
        form = LoginForm()
        return render(request, 'login.html',{'form': form})

def logout_view(request):
    logout(request)
    return redirect('auth:login')



# class CustomLoginView(LoginView):
#     template_name = 'login.html'
#     form_class = LoginForm
#     success_url = reverse_lazy('event:home')

#     def form_valid(self, form):
#         response = super().form_valid(form)
#         if self.request.user.is_superuser:
#             return redirect('event:created-events-list')
#         return response

#     def form_invalid(self, form):
#         messages.error(self.request, 'Invalid email or password.')
#         return redirect('auth:login')

# class CustomLogoutView(LogoutView):
#     next_page = reverse_lazy('auth:login')
