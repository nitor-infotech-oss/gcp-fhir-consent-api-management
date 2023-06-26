import json

from django.http import JsonResponse
from django.shortcuts import render

from .models import ConsentRequest
from .utils import create_consent, get_consent, get_data


def index(request):
    if request.method != "POST":
        message = " "
        return render(request, 'index.html', {'message': message})

    userid = request.POST.get("userid")
    role = request.POST.get("roles")

    if not userid or not role:
        message = "User id is not provided"
        return render(request, 'index.html', {'message': message})

    if 'checkConsent' in request.POST:
        cr = ConsentRequest.objects.filter(patientid=userid, requestedrole=role, status__in=['Pending', 'Approved'])
        if not cr:
            nomessage = "No records of user consent for the requested role. \nTo request for user consent click the 'Request Consent' button above"
            return render(request, 'index.html', {'nomessage': nomessage, 'userid': userid, 'roles': role})

        if not cr[0].consentid:
            return render(request, 'index.html', {'requests': cr, 'userid': userid, 'roles': role})

        resp = get_consent(cr[0].consentid)
        if resp.get('error'):
            nomessage = resp.get('message', 'Something went wrong during checking consent')
            if nomessage in ['Consent Expired', 'Consent not allowed without any expiry']:
                cr.update(status='Expired')
            return render(request, 'index.html', {'nomessage': nomessage, 'userid': userid, 'roles': role})

        expireTime = resp.get('data', {}).get('expireTime')
        return render(request, 'index.html', {'requests': cr, 'expireTime': expireTime})
    elif 'requestConsent' in request.POST:
        pending_requests = ConsentRequest.objects.filter(patientid=userid, requestedrole=role, status="Pending")
        if pending_requests:
            message = "There is a pending request for user consent with same role."
            return render(request, 'index.html', {'message': message})

        cr = ConsentRequest.objects.create(patientid=userid, requestedrole=role, status='Pending')
        return render(request, 'index.html', {'requests': [cr]})


def consentapproval(request):
    if request.method == 'POST' and 'approve' in request.POST:
        requestid = request.POST.get('approve')
        ttl = request.POST.get(requestid+'_ttl')
        cr = ConsentRequest.objects.filter(id=requestid)
        resp = create_consent(cr[0].patientid, cr[0].requestedrole, ttl)
        if resp.get('error'):
            message = resp.get('message', 'Something went wrong during consent creation, please try again')
            return render(request, 'consentapproval.html', {'message': message, 'requests': cr})

        cr.update(consentid=resp.get('data', {}).get('consent_id', ''), status='Approved')
    elif request.method == 'POST' and 'reject' in request.POST:
        requestid = request.POST.get('reject')
        ConsentRequest.objects.filter(id=requestid).update(status='Rejected')

        cr = ConsentRequest.objects.filter(status__in=['Pending']).order_by('-timestamp')
        if cr:
            return render(request, 'consentapproval.html', {'requests': cr})

        message = "No records found"
        return render(request, 'consentapproval.html', {'message': message})

    cr = ConsentRequest.objects.filter(status__in=['Pending']).order_by('-timestamp')
    if cr:
        return render(request, 'consentapproval.html', {'requests': cr})

    message = "No records found"
    return render(request, 'consentapproval.html', {'message': message})


def displaydata(request, requestid):
    cr = ConsentRequest.objects.filter(id=requestid)
    resp = get_data(cr[0].patientid, cr[0].requestedrole, cr[0].consentid)
    if resp.get('error'):
        if resp.get('message', '') == 'Consent Expired':
            cr.update(status='Expired')
        return JsonResponse(resp, safe=False)
    return JsonResponse(resp, safe=False)
