from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
import uuid

class Student(models.Model):
    student_id = models.CharField(max_length=20, primary_key=True)
    name = models.CharField(max_length=100)
    class_name = models.CharField(max_length=20)
    roll_no = models.CharField(max_length=20, unique=True)
    email = models.EmailField(max_length=100, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.name} ({self.student_id})"
    
    class Meta:
        ordering = ['class_name', 'roll_no']

class Subject(models.Model):
    subject_id = models.CharField(max_length=20, primary_key=True)
    subject_name = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.subject_name
    
    class Meta:
        ordering = ['subject_name']

class Result(models.Model):
    GRADE_CHOICES = [
        ('A+', 'A+'), ('A', 'A'), ('A-', 'A-'),
        ('B+', 'B+'), ('B', 'B'), ('B-', 'B-'),
        ('C+', 'C+'), ('C', 'C'), ('D', 'D'),
        ('F', 'F'),
    ]
    
    result_id = models.AutoField(primary_key=True)
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='results')
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='results')
    marks = models.DecimalField(max_digits=5, decimal_places=2)
    grade = models.CharField(max_length=2, choices=GRADE_CHOICES, blank=True)
    total_marks = models.DecimalField(max_digits=5, decimal_places=2, default=100)
    percentage = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['student', 'subject']
        ordering = ['student', 'subject']
    
    def save(self, *args, **kwargs):
        # Calculate percentage
        if self.marks and self.total_marks:
            self.percentage = (self.marks / self.total_marks) * 100
            
            # Calculate grade based on percentage
            if self.percentage >= 90:
                self.grade = 'A+'
            elif self.percentage >= 80:
                self.grade = 'A'
            elif self.percentage >= 75:
                self.grade = 'A-'
            elif self.percentage >= 70:
                self.grade = 'B+'
            elif self.percentage >= 65:
                self.grade = 'B'
            elif self.percentage >= 60:
                self.grade = 'B-'
            elif self.percentage >= 55:
                self.grade = 'C+'
            elif self.percentage >= 50:
                self.grade = 'C'
            elif self.percentage >= 40:
                self.grade = 'D'
            else:
                self.grade = 'F'
        
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.student.name} - {self.subject.subject_name}: {self.marks}"