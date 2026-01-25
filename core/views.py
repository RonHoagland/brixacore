from django.shortcuts import render
from django.contrib.auth.decorators import login_required, user_passes_test

@login_required
def dashboard_view(request):
    """
    Main dashboard view for the core application.
    """
    context = {
        # Placeholder data for future widgets
        "recent_items": [],
        "notifications": [],
    }
    return render(request, "core/dashboard.html", context)

@login_required
@user_passes_test(lambda u: u.is_staff or u.is_superuser)
def admin_home_view(request):
    """
    Landing page for the custom Administration Area.
    """
    return render(request, "core/admin_home.html")

from .models import Preference
from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect

@login_required
@user_passes_test(lambda u: u.is_staff or u.is_superuser)
def preference_list_view(request):
    preferences = Preference.objects.all()
    return render(request, "core/preference_list.html", {"preferences": preferences})

@login_required
@user_passes_test(lambda u: u.is_staff or u.is_superuser)
def preference_update_view(request, pk):
    pref = get_object_or_404(Preference, pk=pk)
    
    if request.method == "POST":
        new_value = request.POST.get('value')
        if new_value is not None:
            pref.value = new_value
            pref.save()
            messages.success(request, f"Preference '{pref.name}' updated.")
            return redirect('preference_list')
            
    return render(request, "core/preference_form.html", {"pref": pref})
