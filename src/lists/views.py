from django.shortcuts import render, redirect
from lists.models import Item, List
from lists.forms import ItemForm, ExistingListItemForm
from django.contrib.auth import get_user_model


User = get_user_model()

# Create your views here.


def home_page(request):
    return render(request, "home.html", {"form": ItemForm()})


def view_list(request, list_id):
    our_list = List.objects.get(id=list_id)
    form = ExistingListItemForm(for_list=our_list)
    if request.method == "POST":
        form = ExistingListItemForm(for_list=our_list, data=request.POST)
        if form.is_valid():
            form.save()
            return redirect(our_list)
    else:
        form = ExistingListItemForm(for_list=our_list)

    return render(request, "list.html", {"list": our_list, "form": form})


def new_list(request):
    form = ItemForm(data=request.POST)
    if form.is_valid():
        nulist = List.objects.create()
        if request.user.is_authenticated:
            nulist.owner = request.user
            nulist.save()
        form.save(for_list=nulist)
        return redirect(nulist)
    else:
        return render(request, "home.html", {"form": form})


def my_lists(request, email):
    owner = User.objects.get(email=email)
    return render(request, "my_lists.html", {"owner": owner})

def share_list(request, list_id):
    my_list = List.objects.get(id=list_id)
    my_list.add(request.POST["sharee"])
    return redirect(my_list)
