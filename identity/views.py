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
    all_roles = Role.objects.all()
    user_role_ids = user_obj.user_roles.values_list('role_id', flat=True)
    available_roles = all_roles.exclude(id__in=user_role_ids)
    
    if request.method == "POST":
        action = request.POST.get('action')
        
        if action == 'toggle_active':
            user_obj.is_active = not user_obj.is_active
            user_obj.save()
            messages.success(request, f"User {user_obj.username} active status changed.")
        
        elif action == 'add_role':
            role_id = request.POST.get('role_id')
            if role_id:
                try:
                    role_obj = Role.objects.get(id=role_id)
                    UserRole.objects.create(
                        user=user_obj, 
                        role=role_obj,
                        created_by=request.user,
                        updated_by=request.user
                    )
                    messages.success(request, f"Role '{role_obj.name}' assigned.")
                except Exception as e:
                    messages.error(request, f"Error assigning role: {e}")
        
        elif action == 'remove_role':
            role_id = request.POST.get('role_id')
            if role_id:
                try:
                    # Use delete behavior for UserRole (hard delete is fine for assignment table, 
                    # but if we want soft delete we should check BaseModel. 
                    # Assuming hard delete for now as UserRole is a join table)
                    UserRole.objects.filter(user=user_obj, role_id=role_id).delete()
                    messages.success(request, "Role removed.")
                except Exception as e:
                    messages.error(request, f"Error removing role: {e}")

        return redirect('user_detail', pk=pk)
            
    return render(request, "identity/user_detail.html", {
        "user_obj": user_obj,
        "available_roles": available_roles
    })

@login_required
@user_passes_test(lambda u: u.is_staff or u.is_superuser)
def role_list_view(request):
    roles = Role.objects.all()
    return render(request, "identity/role_list.html", {"roles": roles})

@login_required
@user_passes_test(lambda u: u.is_staff or u.is_superuser)
def role_create_view(request):
    if request.method == "POST":
        name = request.POST.get('name')
        key = request.POST.get('key')
        description = request.POST.get('description')
        
        if name and key:
            try:
                Role.objects.create(
                    name=name,
                    key=key,
                    description=description,
                    is_system=False,
                    created_by=request.user,
                    updated_by=request.user
                )
                messages.success(request, f"Role '{name}' created.")
                return redirect('role_list')
            except Exception as e:
                messages.error(request, f"Error creating role: {e}")
        else:
            messages.error(request, "Name and Key are required.")
            
    return render(request, "identity/role_form.html")
