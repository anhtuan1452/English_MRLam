from django.shortcuts import render, redirect

from exercise_admin.forms import BaiTapForm


# Create your views here.
def admin_ql_baitap(request):
    return render(request, 'ql_baitap.html')

def them_baitap(request):
    if request.method == 'POST':
        form = BaiTapForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('ql_baitap.html')
    else:
        form = BaiTapForm()
    return render(request, 'thembt.html', {'form': form})



