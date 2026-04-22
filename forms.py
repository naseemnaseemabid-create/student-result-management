from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import AuthenticationForm
from .models import Student, Subject, Result

class LoginForm(AuthenticationForm):
    """Admin login form"""
    username = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Username',
            'required': True
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Password',
            'required': True
        })
    )
    
    class Meta:
        fields = ['username', 'password']

class StudentForm(forms.ModelForm):
    """Student form for adding/editing students"""
    class Meta:
        model = Student
        fields = ['student_id', 'name', 'class_name', 'roll_no', 'email']
        widgets = {
            'student_id': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter Student ID (e.g., STU001)'
            }),
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter Full Name'
            }),
            'class_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter Class (e.g., 10, 12, etc.)'
            }),
            'roll_no': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter Roll Number'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter Email Address'
            }),
        }
    
    def clean_student_id(self):
        student_id = self.cleaned_data.get('student_id')
        if student_id:
            # Check if student_id already exists
            if Student.objects.filter(student_id=student_id).exists():
                if self.instance.pk != student_id:
                    raise forms.ValidationError('Student ID already exists!')
        return student_id
    
    def clean_roll_no(self):
        roll_no = self.cleaned_data.get('roll_no')
        if roll_no:
            # Check if roll_no already exists
            if Student.objects.filter(roll_no=roll_no).exists():
                if self.instance.roll_no != roll_no:
                    raise forms.ValidationError('Roll Number already exists!')
        return roll_no
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email and not email.endswith(('.com', '.edu', '.org')):
            raise forms.ValidationError('Please enter a valid email address')
        return email

class SubjectForm(forms.ModelForm):
    """Subject form for adding/editing subjects"""
    class Meta:
        model = Subject
        fields = ['subject_id', 'subject_name']
        widgets = {
            'subject_id': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter Subject ID (e.g., MATH101)'
            }),
            'subject_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter Subject Name (e.g., Mathematics)'
            }),
        }
    
    def clean_subject_id(self):
        subject_id = self.cleaned_data.get('subject_id')
        if subject_id:
            # Check if subject_id already exists
            if Subject.objects.filter(subject_id=subject_id).exists():
                if self.instance.pk != subject_id:
                    raise forms.ValidationError('Subject ID already exists!')
        return subject_id
    
    def clean_subject_name(self):
        subject_name = self.cleaned_data.get('subject_name')
        if subject_name and len(subject_name) < 2:
            raise forms.ValidationError('Subject name must be at least 2 characters long')
        return subject_name

class ResultForm(forms.ModelForm):
    """Result form for adding/editing marks"""
    class Meta:
        model = Result
        fields = ['student', 'subject', 'marks', 'total_marks']
        widgets = {
            'student': forms.Select(attrs={
                'class': 'form-control'
            }),
            'subject': forms.Select(attrs={
                'class': 'form-control'
            }),
            'marks': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'placeholder': 'Enter marks obtained'
            }),
            'total_marks': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'placeholder': 'Enter total marks (default: 100)'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Set default total_marks to 100 if not provided
        if not self.instance.pk and not self.data.get('total_marks'):
            self.fields['total_marks'].initial = 100
    
    def clean_marks(self):
        marks = self.cleaned_data.get('marks')
        if marks is not None:
            if marks < 0:
                raise forms.ValidationError('Marks cannot be negative!')
        return marks
    
    def clean_total_marks(self):
        total_marks = self.cleaned_data.get('total_marks')
        if total_marks is not None:
            if total_marks <= 0:
                raise forms.ValidationError('Total marks must be greater than zero!')
        return total_marks
    
    def clean(self):
        cleaned_data = super().clean()
        marks = cleaned_data.get('marks')
        total_marks = cleaned_data.get('total_marks')
        
        if marks is not None and total_marks is not None:
            if marks > total_marks:
                raise forms.ValidationError(f'Marks cannot exceed total marks ({total_marks})!')
        
        # Check for duplicate entry
        student = cleaned_data.get('student')
        subject = cleaned_data.get('subject')
        
        if student and subject:
            # For existing instance, exclude itself from duplicate check
            existing = Result.objects.filter(student=student, subject=subject)
            if self.instance.pk:
                existing = existing.exclude(pk=self.instance.pk)
            
            if existing.exists():
                raise forms.ValidationError(
                    f'Result for {student.name} in {subject.subject_name} already exists!'
                )
        
        return cleaned_data

class SearchForm(forms.Form):
    """Search form for filtering students"""
    search_query = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Search by name, roll number, or student ID...'
        })
    )
    class_name = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Filter by class...'
        })
    )