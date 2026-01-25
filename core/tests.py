"""
Core Model Tests - Verify BaseModel and System Configuration models
"""

import pytest
from django.contrib.auth import get_user_model
from core.models import BaseModel, LifecycleModel, Preference, ValueList, ValueListItem

User = get_user_model()


@pytest.mark.django_db
class TestPreference:
    """Test Preference model"""
    
    def test_create_preference(self):
        """Test creating a preference with required fields"""
        user = User.objects.create_user(username='testuser', password='testpass')
        
        pref = Preference.objects.create(
            key='test.preference',
            name='Test Preference',
            description='A test preference',
            data_type='string',
            value='test_value',
            default_value='default_value',
            created_by=user,
            updated_by=user
        )
        
        assert pref.id is not None
        assert pref.key == 'test.preference'
        assert pref.is_active is True
        assert pref.created_at is not None
        assert pref.updated_at is not None


@pytest.mark.django_db
class TestValueList:
    """Test ValueList and ValueListItem models"""
    
    def test_create_value_list(self):
        """Test creating a value list"""
        user = User.objects.create_user(username='testuser', password='testpass')
        
        vl = ValueList.objects.create(
            key='test.list',
            name='Test List',
            description='A test value list',
            created_by=user,
            updated_by=user
        )
        
        assert vl.id is not None
        assert vl.key == 'test.list'
        assert vl.is_active is True
    
    def test_create_value_list_item(self):
        """Test creating a value list item"""
        user = User.objects.create_user(username='testuser', password='testpass')
        
        vl = ValueList.objects.create(
            key='status.list',
            name='Status List',
            created_by=user,
            updated_by=user
        )
        
        item = ValueListItem.objects.create(
            value_list=vl,
            value='active',
            display_label='Active',
            sort_order=1,
            created_by=user,
            updated_by=user
        )
        
        assert item.id is not None
        assert item.value == 'active'
        assert item.is_active is True
        assert str(item) == "Status List: Active"
