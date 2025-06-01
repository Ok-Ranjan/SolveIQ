from django.shortcuts import render
from django.http import *
from OTS.models import *
import random

def welcome(request):
    return render(request,'welcome.html')

def candidateRegistrationForm(request):
    res = render(request,'registration_form.html')
    return res

def candidateRegistration(request):
    if request.method=='POST':
        username = request.POST['username']
        #Check if the user alreday exits
        if len(Candidate.objects.filter(username=username)):
            userStatus=1
        else:
            candidate=Candidate()
            candidate.username=username
            candidate.password=request.POST['password']
            candidate.name=request.POST['name']
            candidate.save()
            userStatus=2
    else:
        userStatus=3 #Request method is not POST
    context={
        'userStatus':userStatus
    }
    return render(request, 'registration.html',context)
 
def loginView(request):
    if request.method=='POST':
        username=request.POST['username']
        password=request.POST['password']
        candidate=Candidate.objects.filter(username=username,password=password)
        if len(candidate)==0:
            loginError="Invaild Username or Password"
            res=render(request,'login.html',{'loginError':loginError})
        else:
            #login Success
            request.session['username']=candidate[0].username #making a session variable , exits until user not logout, and we can use this any views
            request.session['name']=candidate[0].name
            res=HttpResponseRedirect("home")
    else:
        res=render(request,'login.html')
    return res

def candidateHome(request):
    #chack that user come this page with login
    if 'name' not in request.session.keys():
        res=HttpResponseRedirect("login")
    else:
        res=render(request,'home.html')
    return res

def testPaper(request):
    #chack that user come this page with login
    if 'name' not in request.session.keys():
        res=HttpResponseRedirect("login")
    
    #fetch question from database table
    n=int(request.GET['n'])
    question_pool=list(Question.objects.all())
    random.shuffle(question_pool) #all the data inside the list got scattered
    questions_list=question_pool[:n]
    context={'questions':questions_list}
    res=render(request,'test_paper.html',context)
    return res

def calculateTestResult(request):
    #chack that user come this page with login
    if 'name' not in request.session.keys():
        res=HttpResponseRedirect("login")

    total_attempt=0
    total_right=0
    total_wrong=0
    qid_list=[]
    for k in request.POST:
        if k.startswith('qno'):
            qid_list.append(int(request.POST[k]))
    for n in qid_list:
        question=Question.objects.get(qid=n)
        try:
            if question.ans==request.POST['q'+str(n)]:
                total_right+=1
            else:
                total_wrong+=1
            total_attempt+=1
        except:
            pass
    points=(total_right-total_wrong)/len(qid_list)*10
    #store result in Result Table
    result=Result()
    result.username=Candidate.objects.get(username=request.session['username'])
    result.attempt=total_attempt
    result.right=total_right
    result.wrong=total_wrong
    result.points=points
    result.save()
    
    #update Candidate Table
    candidate=Candidate.objects.get(username=request.session['username'])
    candidate.test_attempted=+1
    candidate.points=(candidate.points*(candidate.test_attempted-1)+points)/candidate.test_attempted
    candidate.save()
    res = HttpResponseRedirect("result")
    return res

def testResultHistory(request):
    #chack that user come this page with login
    if 'name' not in request.session.keys():
        res=HttpResponseRedirect("login")

    candidate=Candidate.objects.filter(username=request.session['username'])
    results=Result.objects.filter(username_id=candidate[0].username)
    context={'candidate':candidate[0],'results':results}
    res=render(request,'candidate_history.html',context)
    return res

def showtestResult(request):
    #chack that user come this page with login
    if 'name' not in request.session.keys():
        res=HttpResponseRedirect("login")
    
    #fetch latest result form Result table
    result=Result.objects.filter(resultid=Result.objects.latest('resultid').resultid,username_id=request.session['username'])
    context={'result':result}
    res=render(request,'show_result.html',context)
    return res

def logoutView(request):
    #chack that user come this page with login
    if 'name' in request.session.keys():
        del request.session['username']
        del request.session['name']
    res=HttpResponseRedirect("login")
    return res