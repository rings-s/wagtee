#!/usr/bin/env python
"""
Simple script to create superuser with English prompts.
Arabic is used only in frontend interface.
"""
import os
import sys
import django
from getpass import getpass

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'wagtee.settings')
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
django.setup()

from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from accounts.models import User


def create_superuser():
    print("Create Superuser - English Interface")
    print("===================================")
    
    # Get email
    while True:
        email = input("Email: ").strip()
        if not email:
            print("Email is required.")
            continue
        
        try:
            validate_email(email)
            if User.objects.filter(email=email).exists():
                print(f"User with email '{email}' already exists.")
                continue
            break
        except ValidationError:
            print("Invalid email format.")
    
    # Get names
    first_name = input("First name: ").strip()
    last_name = input("Last name: ").strip()
    
    # Get password
    while True:
        password = getpass("Password: ")
        if not password:
            print("Password is required.")
            continue
        
        confirm_password = getpass("Password (again): ")
        if password != confirm_password:
            print("Passwords do not match.")
            continue
        
        if len(password) < 8:
            print("Password must be at least 8 characters long.")
            continue
        
        break
    
    # Create user
    try:
        user = User.objects.create_superuser(
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name
        )
        print(f"\nSuperuser '{email}' created successfully!")
        print(f"Name: {user.get_full_name()}")
        print(f"Role: {user.role}")
        print(f"Staff: {user.is_staff}")
        print(f"Superuser: {user.is_superuser}")
        
    except Exception as e:
        print(f"Error creating superuser: {e}")
        return False
    
    return True


if __name__ == "__main__":
    try:
        create_superuser()
    except KeyboardInterrupt:
        print("\nOperation cancelled.")
    except Exception as e:
        print(f"Unexpected error: {e}")