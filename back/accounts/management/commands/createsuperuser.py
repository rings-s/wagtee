"""
Custom createsuperuser command with English prompts.
Arabic is used only in the frontend interface.
"""
from django.contrib.auth.management.commands import createsuperuser
from django.core.management.base import CommandError
from django.core.validators import validate_email
from django.contrib.auth import get_user_model

User = get_user_model()


class Command(createsuperuser.Command):
    help = 'Create a superuser with English prompts'

    def add_arguments(self, parser):
        super().add_arguments(parser)
        parser.add_argument(
            '--email',
            help='Specifies the email for the superuser.',
        )
        parser.add_argument(
            '--first_name',
            help='Specifies the first name for the superuser.',
        )
        parser.add_argument(
            '--last_name', 
            help='Specifies the last name for the superuser.',
        )

    def handle(self, *args, **options):
        email = options.get('email')
        first_name = options.get('first_name')
        last_name = options.get('last_name')
        password = options.get('password')
        database = options.get('database')

        # Interactive prompts in English
        if not email:
            email = input('Email: ')
            
        if not email:
            raise CommandError('Email is required.')
            
        try:
            validate_email(email)
        except Exception:
            raise CommandError('Invalid email format.')

        if not first_name:
            first_name = input('First name: ')
            
        if not last_name:
            last_name = input('Last name: ')

        if not password:
            password = self._get_input_message('Password: ', hidden=True)
            confirm_password = self._get_input_message('Password (again): ', hidden=True)
            
            if password != confirm_password:
                raise CommandError('Passwords do not match.')

        # Check if user already exists
        try:
            User._default_manager.db_manager(database).get(email=email)
            raise CommandError(f'User with email "{email}" already exists.')
        except User.DoesNotExist:
            pass

        # Create superuser
        try:
            user = User._default_manager.db_manager(database).create_superuser(
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name,
                username=email  # Set username to email
            )
            
            if options.get('verbosity', 1) >= 1:
                self.stdout.write(
                    self.style.SUCCESS(f'Superuser "{email}" created successfully.')
                )
                
        except Exception as e:
            raise CommandError(f'Error creating superuser: {e}')

    def _get_input_message(self, message, hidden=False):
        """Get input with optional hidden mode for passwords"""
        if hidden:
            import getpass
            return getpass.getpass(message)
        else:
            return input(message)