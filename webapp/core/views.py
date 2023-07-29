from django.shortcuts import render, redirect

from core.forms import ProducedForm
from core.models import ProducedModel


def produced_model_list(request):
    produced_models = ProducedModel.objects.all()
    return render(request, 'include/content.html', {'produced_models': produced_models})

def produced_new(request):
    if request.method == 'POST':
        form = ProducedForm(request.POST)
        print(form.data)
    else:
        form = ProducedForm()
    return render(request, 'include/testify_form.html', {'form': form})


