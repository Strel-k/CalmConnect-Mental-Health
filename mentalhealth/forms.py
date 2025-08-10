from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm  # Added AuthenticationForm here
from .models import CustomUser
from django.core.validators import RegexValidator 
from .models import Appointment, Report, Counselor


class CustomUserRegistrationForm(UserCreationForm):
    email_prefix = forms.CharField(
        max_length=50,
        validators=[RegexValidator(
            regex=r'^[a-zA-Z0-9._\-]+$',  # Fixed regex pattern
            message='Only letters, numbers, dots, hyphens, and underscores allowed'
        )],
        required=True
    )
    
    class Meta:
        model = CustomUser
        fields = ('username', 'password1', 'password2', 
                 'student_id', 'age', 'full_name', 'gender',
                 'college', 'program', 'year_level')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Set clear password requirements
        self.fields['password1'].help_text = '''
        <div class="password-requirements">
            <strong>Password Requirements:</strong>
            <ul>
                <li>At least 12 characters long</li>
                <li>Contains at least one uppercase letter (A-Z)</li>
                <li>Contains at least one lowercase letter (a-z)</li>
                <li>Contains at least one number (0-9)</li>
                <li>Contains at least one special character (@$!%*?&)</li>
                <li>Cannot be too similar to your username</li>
                <li>Cannot be entirely numeric</li>
            </ul>
        </div>
        '''
        self.fields['password2'].help_text = 'Re-enter the password to confirm.'
        
        # Add placeholder text to password fields
        self.fields['password1'].widget.attrs.update({
            'placeholder': 'Enter your password',
            'class': 'form-control'
        })
        self.fields['password2'].widget.attrs.update({
            'placeholder': 'Confirm your password',
            'class': 'form-control'
        })

    def clean(self):
        cleaned_data = super().clean()
        email_prefix = cleaned_data.get('email_prefix')
        missing_fields = []
        required_fields = ['username', 'password1', 'password2', 'student_id', 'full_name', 'gender', 'college', 'program', 'year_level']
        
        # Handle age field separately since it's a number
        age = cleaned_data.get('age')
        if not age or (isinstance(age, str) and not age.strip()):
            missing_fields.append('age')
        elif isinstance(age, str):
            try:
                age_int = int(age)
                if age_int < 15 or age_int > 100:
                    self.add_error('age', 'Age must be between 15 and 100')
                else:
                    cleaned_data['age'] = age_int
            except ValueError:
                self.add_error('age', 'Age must be a valid number')
        
        for field in required_fields:
            value = cleaned_data.get(field)
            if not value or (isinstance(value, str) and not value.strip()):
                missing_fields.append(field)
        
        if not email_prefix:
            self.add_error('email_prefix', 'This field is required')
        else:
            cleaned_data['email'] = f"{email_prefix}@clsu2.edu.ph"
        
        if missing_fields:
            for field in missing_fields:
                self.add_error(field, 'This field is required')
        
        return cleaned_data
    

    def clean_student_id(self):
        student_id = self.cleaned_data.get('student_id')
        if CustomUser.objects.filter(student_id=student_id).exists():
            raise forms.ValidationError("A user with this Student ID already exists.")
        return student_id

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if CustomUser.objects.filter(email=email).exists():
            raise forms.ValidationError("A user with this email already exists.")
        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.full_name = self.cleaned_data['full_name']
        user.student_id = self.cleaned_data['student_id']
        user.age = self.cleaned_data['age']
        user.gender = self.cleaned_data['gender']
        user.college = self.cleaned_data['college']
        user.program = self.cleaned_data['program']
        user.year_level = self.cleaned_data['year_level']
        
        if commit:
            user.save()
        return user


class CustomLoginForm(AuthenticationForm):
    username = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Username or Email',
            'id': 'username'
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Password',
            'id': 'password'
        })
    )
    remember_me = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={
            'id': 'remember'
        })
    )

    def clean_username(self):
        username = self.cleaned_data.get('username')
        # Allow login with email or username
        if '@' in username:
            try:
                user = CustomUser.objects.get(email=username)
                return user.username
            except CustomUser.DoesNotExist:
                pass
        return username
    
    
class CounselorProfileForm(forms.ModelForm):
    RANK_CHOICES = [
        ("INSTRUCTOR I", "INSTRUCTOR I"),
        ("INSTRUCTOR II", "INSTRUCTOR II"),
        ("INSTRUCTOR III", "INSTRUCTOR III"),
        ("Assistant Professor I", "Assistant Professor I"),
        ("Assistant Professor II", "Assistant Professor II"),
        ("Assistant Professor III", "Assistant Professor III"),
        ("Associate Professor I", "Associate Professor I"),
        ("Associate Professor II", "Associate Professor II"),
        ("Associate Professor III", "Associate Professor III"),
        ("Professor I", "Professor I"),
        ("Professor II", "Professor II"),
        ("Professor III", "Professor III"),
        ("Professor IV", "Professor IV"),
        ("Professor V", "Professor V"),
        ("Professor VI", "Professor VI"),
        ("Professor VII", "Professor VII"),
        ("Professor VIII", "Professor VIII"),
        ("Professor IX", "Professor IX"),
        ("Professor X", "Professor X"),
        ("Professor Emeritus", "Professor Emeritus"),
        ("Counselor", "Counselor"),
    ]

    rank = forms.ChoiceField(
        choices=RANK_CHOICES,
        required=True,
        label="Rank/Title"
    )

    class Meta:
        model = Counselor
        fields = ['unit', 'rank', 'bio', 'image']

class AppointmentForm(forms.ModelForm):
    def __init__(self, counselor, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['user'].queryset = CustomUser.objects.filter(
            appointments__counselor=counselor
        ).distinct()
    
    class Meta:
        model = Appointment
        fields = ['user', 'date', 'time', 'services', 'reason']

class AppointmentStatusForm(forms.ModelForm):
    class Meta:
        model = Appointment
        fields = ['status', 'notes']

class ReportForm(forms.ModelForm):
    class Meta:
        model = Report
        fields = ['user', 'appointment', 'title', 'description', 'report_type']
        widgets = {
            'user': forms.HiddenInput(),
            'appointment': forms.HiddenInput(),
        }