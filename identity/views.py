from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from .models import Role, UserRole

from core.utils import apply_sorting

@login_required
@user_passes_test(lambda u: u.is_staff or u.is_superuser)
def user_list_view(request):
    users = User.objects.all()
    
    # Sorting
    users, sort_field, sort_dir = apply_sorting(
        users, 
        request, 
        allowed_fields=['username', 'email', 'is_active'], 
        default_sort='username', 
        default_dir='asc'
    )
    
    return render(request, "identity/user_list.html", {
        "users": users,
        "current_sort": sort_field,
        "current_dir": sort_dir
    })

@login_required
@user_passes_test(lambda u: u.is_staff or u.is_superuser)
def user_detail_view(request, pk):
    user_obj = get_object_or_404(User, pk=pk)
    
    if request.method == "POST":
        # Handle simple updates (toggle active, etc)
        action = request.POST.get('action')
        if action == 'toggle_active':
            user_obj.is_active = not user_obj.is_active
            user_obj.save()
            messages.success(request, f"User {user_obj.username} active status changed.")
            return redirect('user_detail', pk=pk)
            
    return render(request, "identity/user_detail.html", {"user_obj": user_obj})
