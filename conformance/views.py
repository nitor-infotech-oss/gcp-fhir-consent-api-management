import json

from django.shortcuts import render

from .utils import create_data, get_fhir_metadata


def upload_resource(request):
    if request.method == 'POST':
        json_file = request.FILES['json_file']
        if not json_file:
            return render(request, 'manageresources.html', {'message': 'Please upload valid json file.'})

        try:
            data = json.load(json_file)
        except Exception as exc:
            message = str(exc)
        else:
            resp = create_data(data)
            if resp.get('error'):
                message = resp.get('message', 'File upload not succeeded.')
            else:
                message = resp.get('message', 'Success')
        return render(request, 'manageresources.html', {'message': message})
    else:
        return render(request, 'manageresources.html')


def get_capability_statement(request):
    resp = get_fhir_metadata()
    if resp.get('error'):
        message = resp.get('message', 'Error fetching capability statement')
        return render(request, 'capabilitystatement.html', {'message': message})
    return render(request, 'capabilitystatement.html', {'requests': json.dumps(resp.get('data', {}))})
