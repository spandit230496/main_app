

from django.shortcuts import render
from .models import Period
from django.db.models import Q
from datetime import datetime
from django.contrib.auth.decorators import login_required
import matplotlib.pyplot as plt
import base64
import time
from io import BytesIO
from django.http import HttpResponse
from django.shortcuts import redirect
from datetime import datetime

@login_required
def period_record_view(request):
    if request.method == 'POST':
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')
        symptoms = request.POST.get('symptoms')
        other_info = request.POST.get('other_info') 
        user = request.user

        end_date_str = request.POST.get('end_date')
        end_date = datetime.strptime(end_date_str, '%Y-%m-%d')
        end_date_epoch_ms = int(time.mktime(end_date.timetuple()) * 1000)

        start_date_str= request.POST.get('start_date')
        start_date = datetime.strptime(start_date_str, '%Y-%m-%d')
        start_date_epoch_ms= int(time.mktime(start_date.timetuple()) * 1000)

        date_now_epoch =int(datetime.now().timestamp())

        # if end_date_epoch_ms > date_now_epoch:
        #     return render(request, 'record_your_cramps.html', {'error': 'End date cannot be in the past!'})
        
        # if start_date_epoch_ms > date_now_epoch:
        #     return render(request, 'record_your_cramps.html', {'error': 'Start date cannot be in the Future!'})
        
        period = Period.objects.create(user=user, start_date=start_date, end_date=end_date, symptoms=symptoms, other_info=other_info)

    period_records = Period.objects.filter(user=request.user)
    return render(request, 'record_your_cramps.html', {'period_records': period_records})

def period_list_view(request):
    start_date = request.POST.get('start_date')
    end_date = request.POST.get('end_date')

    period_records = Period.objects.all()

    if start_date:
        start_date = datetime.strptime(start_date, '%Y-%m-%d')
        period_records = period_records.filter(start_date__gte=start_date)

    if end_date:
        end_date = datetime.strptime(end_date, '%Y-%m-%d')
        period_records = period_records.filter(end_date__lte=end_date)

    return render(request, 'get_list.html', {'period_records': period_records})

def period_home_page_view(request):
    return render(request, 'home.html')


def generate_plot(request):
    period_records = Period.objects.filter(user=request.user)

    durations = []  
    months = []  
    total_duration=0
    average_duration=0

    for period in period_records:
        duration = (period.end_date - period.start_date).days
        total_duration+=duration
        durations.append(duration)
        months.append(period.start_date.strftime('%B'))  
         

    average_duration=total_duration//len(durations)

    plt.figure(figsize=(10, 6))
    plt.scatter(months, durations, color='skyblue')
    plt.xlabel('Month')
    plt.ylabel('Duration (Days)')
    plt.title('Relationship between Cramp Durations and Months')

    buffer = BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    plot_data = base64.b64encode(buffer.getvalue()).decode()
    buffer.close()

    return plot_data, average_duration

def get_visual_data_view(request):
    plot_data , average_duration= generate_plot(request)
    return render(request, 'get_visual_data.html', {'plot_data': plot_data, 'average_duration': average_duration})

def delete_period(request, period_id):
    period = Period.objects.get(id=period_id)
    if request.method == 'POST':
        period.delete()
        return redirect('/period_list/')
    else:
        return HttpResponse("Invalid request method.")
    



