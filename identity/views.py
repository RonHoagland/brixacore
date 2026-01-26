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

@login_required
@user_passes_test(lambda u: u.is_staff or u.is_superuser)
@login_required
@user_passes_test(lambda u: u.is_staff or u.is_superuser)
def role_delete_confirm_view(request, user_id, role_id):
    """
    Confirmation page view for role deletion.
    GET: Show confirmation page.
    POST: Delete role and redirect.
    """
    try:
        user_obj = get_object_or_404(User, pk=user_id)
        role_obj = get_object_or_404(Role, pk=role_id)
        
        if request.method == "POST":
            UserRole.objects.filter(user=user_obj, role=role_obj).delete()
            messages.success(request, f"Role '{role_obj.name}' removed from {user_obj.username}.")
            return redirect('user_detail', pk=user_id)
            
        return render(request, "identity/role_delete_confirm.html", {
            "target_user": user_obj,
            "role": role_obj
        })
        
    except Exception as e:
        messages.error(request, f"Error preparing removal: {e}")
        return redirect('user_detail', pk=user_id)

@login_required
@user_passes_test(lambda u: u.is_staff or u.is_superuser)
def role_delete_view(request, pk):
    """
    Delete a custom role definition.
    Protected: Cannot delete System roles or roles assigned to users.
    """
    try:
        role = get_object_or_404(Role, pk=pk)
        
        # System Role Check
        if role.is_system:
            messages.error(request, f"Cannot delete system role '{role.name}'.")
            return redirect('role_list')
            
        # Assignment Check
        if role.assigned_users.exists():
            messages.error(request, f"Cannot delete role '{role.name}' because it is assigned to users. Unassign it first.")
            return redirect('role_list')
        
        if request.method == "POST":
            role.delete()
            messages.success(request, f"Role '{role.name}' deleted.")
            return redirect('role_list')
            
        return render(request, "identity/role_definition_delete_confirm.html", {"role": role})
        
    except Exception as e:
        messages.error(request, f"Error deleting role: {e}")
        return redirect('role_list')

@login_required
@user_passes_test(lambda u: u.is_staff or u.is_superuser)
def user_delete_view(request, pk):
    """
    Delete a user with smart audit checking.
    
    Allows deletion if user only has login records (Session).
    Blocks deletion if user has transaction history or other protected records.
    """
    from django.db.models import ProtectedError
    from audit.models import UserTransaction
    
    try:
        user_obj = get_object_or_404(User, pk=pk)
        
        # Self-Check
        if user_obj.id == request.user.id:
            messages.error(request, "You cannot delete your own account.")
            return redirect('user_list')
        
        # Smart Audit Check: Block if user has transaction history
        has_transactions = UserTransaction.objects.filter(user=user_obj).exists()
        
        if has_transactions:
            messages.error(
                request, 
                f"Cannot delete user '{user_obj.username}' because they have transaction history (created or deleted records). "
                "Users with action history must be preserved for audit integrity."
            )
            return redirect('user_list')
            
        if request.method == "POST":
            try:
                username = user_obj.username
                # Sessions will CASCADE delete automatically
                # Other protected relationships will still raise ProtectedError
                user_obj.delete()
                messages.success(request, f"User '{username}' deleted successfully.")
                return redirect('user_list')
            except ProtectedError as e:
                # Catch any other protected relationships (e.g., created_by fields)
                messages.error(
                    request, 
                    f"Cannot delete user '{user_obj.username}' because they are linked to other records. "
                    "This user may have created files, roles, or other entities that reference them."
                )
                return redirect('user_list')
            except Exception as e:
                messages.error(request, f"Error deleting user: {e}")
                return redirect('user_list')
            
        return render(request, "identity/user_delete_confirm.html", {"target_user": user_obj})
        
    except Exception as e:
        messages.error(request, f"Error preparing user deletion: {e}")
        return redirect('user_list')

