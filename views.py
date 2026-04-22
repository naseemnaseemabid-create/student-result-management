from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, Sum, Avg, Count
from django.http import HttpResponse
from django.core.exceptions import PermissionDenied
from .models import Student, Subject, Result
from .forms import LoginForm, StudentForm, SubjectForm, ResultForm, SearchForm
from decimal import Decimal
import csv

# Helper decorator
def admin_required(view_func):
    """Decorator to check if user is admin"""
    def wrapper(request, *args, **kwargs):
        if request.user.is_authenticated and request.user.is_staff:
            return view_func(request, *args, **kwargs)
        raise PermissionDenied
    return wrapper

def index(request):
    """Home page"""
    return render(request, 'index.html')

def login_view(request):
    """User login"""
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            
            if user is not None:
                login(request, user)
                messages.success(request, f'Welcome back, {username}!')
                return redirect('dashboard')
            else:
                messages.error(request, 'Invalid username or password!')
        else:
            messages.error(request, 'Invalid username or password!')
    else:
        form = LoginForm()
    
    return render(request, 'login.html', {'form': form})

@login_required
def logout_view(request):
    """User logout"""
    logout(request)
    messages.success(request, 'You have been logged out successfully!')
    return redirect('index')

@login_required
def dashboard(request):
    """Admin dashboard"""
    total_students = Student.objects.count()
    total_subjects = Subject.objects.count()
    total_results = Result.objects.count()
    
    # Get class-wise statistics
    class_stats = Student.objects.values('class_name').annotate(
        student_count=Count('student_id')
    ).order_by('class_name')
    
    # Get recent results
    recent_results = Result.objects.select_related('student', 'subject').order_by('-created_at')[:10]
    
    context = {
        'total_students': total_students,
        'total_subjects': total_subjects,
        'total_results': total_results,
        'class_stats': class_stats,
        'recent_results': recent_results,
    }
    return render(request, 'dashboard.html', context)

# Student Management Views
@login_required
@admin_required
def student_list(request):
    """List all students"""
    search_form = SearchForm(request.GET)
    students = Student.objects.all()
    
    if search_form.is_valid():
        search_query = search_form.cleaned_data.get('search_query')
        class_name = search_form.cleaned_data.get('class_name')
        
        if search_query:
            students = students.filter(
                Q(name__icontains=search_query) | 
                Q(roll_no__icontains=search_query) |
                Q(student_id__icontains=search_query)
            )
        
        if class_name:
            students = students.filter(class_name__icontains=class_name)
    
    context = {
        'students': students,
        'search_form': search_form,
    }
    return render(request, 'students/student_list.html', context)

@login_required
@admin_required
def add_student(request):
    """Add new student"""
    if request.method == 'POST':
        form = StudentForm(request.POST)
        if form.is_valid():
            student = form.save()
            messages.success(request, f'Student {student.name} added successfully!')
            return redirect('student_list')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = StudentForm()
    
    return render(request, 'students/add_student.html', {'form': form})

@login_required
@admin_required
def edit_student(request, student_id):
    """Edit student details"""
    student = get_object_or_404(Student, student_id=student_id)
    
    if request.method == 'POST':
        form = StudentForm(request.POST, instance=student)
        if form.is_valid():
            form.save()
            messages.success(request, f'Student {student.name} updated successfully!')
            return redirect('student_list')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = StudentForm(instance=student)
    
    return render(request, 'students/edit_student.html', {'form': form, 'student': student})

@login_required
@admin_required
def delete_student(request, student_id):
    """Delete student"""
    student = get_object_or_404(Student, student_id=student_id)
    
    if request.method == 'POST':
        student_name = student.name
        student.delete()
        messages.success(request, f'Student {student_name} deleted successfully!')
        return redirect('student_list')
    
    return render(request, 'students/delete_student.html', {'student': student})

# Subject Management Views
@login_required
@admin_required
def subject_list(request):
    """List all subjects"""
    subjects = Subject.objects.all().order_by('subject_name')
    return render(request, 'subjects/subject_list.html', {'subjects': subjects})

@login_required
@admin_required
def add_subject(request):
    """Add new subject"""
    if request.method == 'POST':
        form = SubjectForm(request.POST)
        if form.is_valid():
            subject = form.save()
            messages.success(request, f'Subject {subject.subject_name} added successfully!')
            return redirect('subject_list')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = SubjectForm()
    
    return render(request, 'subjects/add_subject.html', {'form': form})

@login_required
@admin_required
def edit_subject(request, subject_id):
    """Edit subject details"""
    subject = get_object_or_404(Subject, subject_id=subject_id)
    
    if request.method == 'POST':
        form = SubjectForm(request.POST, instance=subject)
        if form.is_valid():
            form.save()
            messages.success(request, f'Subject {subject.subject_name} updated successfully!')
            return redirect('subject_list')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = SubjectForm(instance=subject)
    
    return render(request, 'subjects/edit_subject.html', {'form': form, 'subject': subject})

@login_required
@admin_required
def delete_subject(request, subject_id):
    """Delete subject"""
    subject = get_object_or_404(Subject, subject_id=subject_id)
    
    if request.method == 'POST':
        subject_name = subject.subject_name
        subject.delete()
        messages.success(request, f'Subject {subject_name} deleted successfully!')
        return redirect('subject_list')
    
    return render(request, 'subjects/delete_subject.html', {'subject': subject})

# Result Management Views
@login_required
@admin_required
def add_result(request):
    """Add student marks"""
    if request.method == 'POST':
        form = ResultForm(request.POST)
        if form.is_valid():
            result = form.save()
            messages.success(request, f'Result for {result.student.name} - {result.subject.subject_name} added successfully!')
            return redirect('dashboard')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = ResultForm()
    
    context = {
        'form': form,
    }
    return render(request, 'results/add_result.html', context)

@login_required
@admin_required
def edit_result(request, result_id):
    """Edit student marks"""
    result = get_object_or_404(Result, result_id=result_id)
    
    if request.method == 'POST':
        form = ResultForm(request.POST, instance=result)
        if form.is_valid():
            form.save()
            messages.success(request, f'Result updated successfully!')
            return redirect('dashboard')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = ResultForm(instance=result)
    
    return render(request, 'results/edit_result.html', {'form': form, 'result': result})

@login_required
@admin_required
def delete_result(request, result_id):
    """Delete student result"""
    result = get_object_or_404(Result, result_id=result_id)
    
    if request.method == 'POST':
        student_name = result.student.name
        subject_name = result.subject.subject_name
        result.delete()
        messages.success(request, f'Result for {student_name} - {subject_name} deleted successfully!')
        return redirect('dashboard')
    
    return render(request, 'results/delete_result.html', {'result': result})

# Result Viewing (For Students)
def view_result(request):
    """Student view their result using roll number"""
    result_data = None
    student = None
    results = None
    
    if request.method == 'POST':
        roll_no = request.POST.get('roll_no')
        try:
            student = Student.objects.get(roll_no=roll_no)
            results = Result.objects.filter(student=student).select_related('subject')
            
            if results.exists():
                # Calculate total marks and percentage
                total_obtained = sum(float(result.marks) for result in results)
                total_max = sum(float(result.total_marks) for result in results)
                overall_percentage = (total_obtained / total_max) * 100 if total_max > 0 else 0
                
                # Determine overall grade
                if overall_percentage >= 90:
                    overall_grade = 'A+'
                elif overall_percentage >= 80:
                    overall_grade = 'A'
                elif overall_percentage >= 75:
                    overall_grade = 'A-'
                elif overall_percentage >= 70:
                    overall_grade = 'B+'
                elif overall_percentage >= 65:
                    overall_grade = 'B'
                elif overall_percentage >= 60:
                    overall_grade = 'B-'
                elif overall_percentage >= 55:
                    overall_grade = 'C+'
                elif overall_percentage >= 50:
                    overall_grade = 'C'
                elif overall_percentage >= 40:
                    overall_grade = 'D'
                else:
                    overall_grade = 'F'
                
                result_data = {
                    'student': student,
                    'results': results,
                    'total_obtained': total_obtained,
                    'total_max': total_max,
                    'overall_percentage': overall_percentage,
                    'overall_grade': overall_grade,
                }
            else:
                messages.error(request, 'No results found for this roll number!')
                
        except Student.DoesNotExist:
            messages.error(request, 'Student not found with this roll number!')
    
    return render(request, 'results/view_result.html', {'result_data': result_data})

# Reports Views
@login_required
def class_report(request):
    """Generate class-wise reports"""
    classes = Student.objects.values_list('class_name', flat=True).distinct().order_by('class_name')
    selected_class = request.GET.get('class_name')
    report_data = None
    
    if selected_class:
        students = Student.objects.filter(class_name=selected_class)
        class_results = []
        
        for student in students:
            results = Result.objects.filter(student=student)
            if results.exists():
                total_obtained = sum(float(result.marks) for result in results)
                total_max = sum(float(result.total_marks) for result in results)
                percentage = (total_obtained / total_max) * 100 if total_max > 0 else 0
                
                class_results.append({
                    'student': student,
                    'total_obtained': total_obtained,
                    'total_max': total_max,
                    'percentage': percentage,
                })
        
        # Sort by percentage
        class_results.sort(key=lambda x: x['percentage'], reverse=True)
        
        # Add rank
        for idx, result in enumerate(class_results, 1):
            result['rank'] = idx
        
        report_data = {
            'class_name': selected_class,
            'results': class_results,
            'total_students': len(class_results),
        }
    
    context = {
        'classes': classes,
        'selected_class': selected_class,
        'report_data': report_data,
    }
    return render(request, 'reports/class_report.html', context)

@login_required
def export_results_csv(request):
    """Export results to CSV"""
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="student_results.csv"'
    
    writer = csv.writer(response)
    writer.writerow(['Student ID', 'Name', 'Class', 'Roll No', 'Subject', 'Marks', 'Total Marks', 'Grade', 'Percentage'])
    
    results = Result.objects.select_related('student', 'subject').all()
    
    for result in results:
        writer.writerow([
            result.student.student_id,
            result.student.name,
            result.student.class_name,
            result.student.roll_no,
            result.subject.subject_name,
            result.marks,
            result.total_marks,
            result.grade,
            f"{result.percentage:.2f}%" if result.percentage else "N/A"
        ])
    
    return response