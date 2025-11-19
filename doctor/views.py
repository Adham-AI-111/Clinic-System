from django.shortcuts import render

# will contain all the system details (appointments, patients, prescriptions, diagnoses), and pages for the system admin

def home(request):
    return render(request, 'doctor/home.html')
