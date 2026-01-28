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
    
    grouped_prefs = {
        'Company Information': [],
        'Financial Settings': [],
        'Localization': [],
        'Email Configuration': [],
        'Backup & Restore': [],
        'System & Other': []
    }
    
    for p in preferences:
        k = p.key
        if k.startswith('company_') or k.startswith('default_logo_') or k.startswith('site_title'):
             grouped_prefs['Company Information'].append(p)
        elif k.startswith('finance_'):
             grouped_prefs['Financial Settings'].append(p)
        elif k.startswith('loc_'):
             grouped_prefs['Localization'].append(p)
        elif k.startswith('email_'):
             grouped_prefs['Email Configuration'].append(p)
        elif k.startswith('backup_') or k.startswith('audit_'):
             grouped_prefs['Backup & Restore'].append(p)
        else:
             grouped_prefs['System & Other'].append(p)
             
    return render(request, "core/preference_list.html", {"grouped_preferences": grouped_prefs})

from .constants import COUNTRY_DEFAULTS
from django.core.files.storage import default_storage

@login_required
@user_passes_test(lambda u: u.is_staff or u.is_superuser)
def preference_update_view(request, pk):
    pref = get_object_or_404(Preference, pk=pk)
    
    # 1. Determine Input Type & Choices
    widget_type = 'text'
    choices = None
    
    if pref.key == 'loc_default_country':
        widget_type = 'select'
        choices = [(k, v['name']) for k, v in COUNTRY_DEFAULTS.items()]
        
    elif pref.key == 'finance_default_currency':
        widget_type = 'select'
        choices = [('USD', 'USD'), ('PHP', 'PHP'), ('EUR', 'EUR'), ('GBP', 'GBP')]
        
    elif pref.key == 'finance_decimal_precision':
        widget_type = 'select'
        choices = [('2', '2 Decimals'), ('3', '3 Decimals')]
        
    elif pref.key == 'loc_timezone':
        widget_type = 'select'
        # Get current country to filter timezones
        country_pref = Preference.objects.filter(key='loc_default_country').first()
        current_country = country_pref.value if country_pref else 'US'
        
        # If country is known, show its timezones
        if current_country in COUNTRY_DEFAULTS:
             t_zones = COUNTRY_DEFAULTS[current_country]['timezones']
             choices = [(tz, tz) for tz in t_zones]
        else:
             choices = [(pref.value, pref.value)]

    elif pref.data_type == 'boolean':
        widget_type = 'select'
        choices = [('true', 'Yes'), ('false', 'No')]

    elif pref.data_type == 'path' and 'logo' in pref.key:
        widget_type = 'file'

    
    if request.method == "POST":
        new_value = request.POST.get('value')
        
        # Handle File Upload
        if widget_type == 'file' and request.FILES.get('value'):
             uploaded_file = request.FILES['value']
             # Save to media/logos
             path = default_storage.save(f'logos/{uploaded_file.name}', uploaded_file)
             new_value = default_storage.url(path)
        
        if new_value is not None:
            pref.value = new_value
            pref.save()
            
            # TRIGGER CASCADES
            if pref.key == 'loc_default_country' and new_value in COUNTRY_DEFAULTS:
                data = COUNTRY_DEFAULTS[new_value]
                # Update Currency
                Preference.objects.filter(key='finance_default_currency').update(value=data['currency'])
                Preference.objects.filter(key='finance_currency_symbol').update(value=data['symbol'])
                # Update Phone
                Preference.objects.filter(key='loc_default_phone_code').update(value=data['phone_code'])
                Preference.objects.filter(key='loc_default_phone_format').update(value=data['phone_format'])
                # Update Date
                Preference.objects.filter(key='loc_date_format').update(value=data['date_format'])
                # Update Timezone (Set to first one)
                if data['timezones']:
                     Preference.objects.filter(key='loc_timezone').update(value=data['timezones'][0])
                     
                messages.success(request, f"Country updated to {data['name']}. Related settings (Currency, Phone, Date, Timezone) auto-updated.")
            else:
                messages.success(request, f"Preference '{pref.name}' updated.")
                
            return redirect('preference_list')
            
    return render(request, "core/preference_form.html", {
        "pref": pref, 
        "widget_type": widget_type, 
        "choices": choices
    })
