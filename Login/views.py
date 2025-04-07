from django.shortcuts import render
def SignUp(request):
    return render(request, 'resgister_content.html')
def SignIn(request):
    return render(request, 'login_content.html')
def ForgetPassword(request):
    return render(request,'forgetpass.html')
def RePassWord(request):
    return render(request,'re-password.html')