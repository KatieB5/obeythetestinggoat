from django.test import TestCase
from lists.models import Item, List
from lists.forms import (
    ItemForm,
    EMPTY_ITEM_ERROR,
    DUPLICATE_ITEM_ERROR,
    ExistingListItemForm,
)
from django.utils.html import escape
from django.contrib.auth import get_user_model

User = get_user_model()

# Create your tests here.
class HomePageTest(TestCase):
    def test_uses_home_template(self):
        response = self.client.get("/")
        self.assertTemplateUsed(response, "home.html")

    def test_only_saves_items_when_necessary(self):
        self.client.get("/")
        self.assertEqual(Item.objects.count(), 0)

    def test_home_page_uses_item_form(self):
        response = self.client.get("/")
        self.assertIsInstance(response.context["form"], ItemForm)


class ListViewTest(TestCase):
    def test_uses_list_template(self):
        correct_list = List.objects.create()
        response = self.client.get(f"/lists/{correct_list.id}/")
        self.assertTemplateUsed(response, "list.html")

    def test_displays_only_items_for_that_list(self):
        correct_list = List.objects.create()
        Item.objects.create(text="itemey 1", list=correct_list)
        Item.objects.create(text="itemey 2", list=correct_list)
        other_list = List.objects.create()
        Item.objects.create(text="other list item", list=other_list)

        response = self.client.get(f"/lists/{correct_list.id}/")

        self.assertContains(response, "itemey 1")
        self.assertContains(response, "itemey 2")
        self.assertNotContains(response, "other list item")

    def test_passes_correct_list_to_template(self):
        other_list = List.objects.create()
        correct_list = List.objects.create()
        response = self.client.get(f"/lists/{correct_list.id}/")
        self.assertEqual(response.context["list"], correct_list)

    def test_can_save_a_POST_request_to_an_existing_list(self):
        other_list = List.objects.create()
        correct_list = List.objects.create()

        self.client.post(
            f"/lists/{correct_list.id}/",
            data={"text": "A new item for an existing list"},
        )

        self.assertEqual(Item.objects.count(), 1)
        new_item = Item.objects.get()
        self.assertEqual(new_item.text, "A new item for an existing list")
        self.assertEqual(new_item.list, correct_list)

    def test_POST_redirects_to_list_view(self):
        other_list = List.objects.create()
        correct_list = List.objects.create()

        response = self.client.post(
            f"/lists/{correct_list.id}/",
            data={"text": "A new item for an existing list"},
        )

        self.assertRedirects(response, f"/lists/{correct_list.id}/")

    def post_invalid_input(self):
        mylist = List.objects.create()
        return self.client.post(
            f"/lists/{mylist.id}/",
            data={"text": ""},
        )

    def test_for_invalid_input_nothing_saved_to_db(self):
        self.post_invalid_input()
        self.assertEqual(Item.objects.count(), 0)

    def test_for_invalid_input_renders_list_template(self):
        response = self.post_invalid_input()
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "list.html")

    def test_for_invalid_input_passes_form_to_template(self):
        response = self.post_invalid_input()
        self.assertIsInstance(response.context["form"], ExistingListItemForm)

    def test_for_invalid_input_shows_error_on_page(self):
        response = self.post_invalid_input()
        self.assertContains(response, escape(EMPTY_ITEM_ERROR))

    def test_duplicate_item_validation_errors_end_up_on_lists_page(self):
        list1 = List.objects.create()
        Item.objects.create(list=list1, text="textey")
        response = self.client.post(
            f"/lists/{list1.id}/",
            data={"text": "textey"},
        )

        expected_error = escape(DUPLICATE_ITEM_ERROR)
        self.assertContains(response, expected_error)
        self.assertTemplateUsed(response, "list.html")
        self.assertEqual(Item.objects.all().count(), 1)

    def test_displays_item_form(self):
        my_list = List.objects.create()
        response = self.client.get(f"/lists/{my_list.id}/")
        self.assertIsInstance(response.context["form"], ExistingListItemForm)
        self.assertContains(response, 'name="text"')

    def test_form_save(self):
        mylist = List.objects.create()
        form = ExistingListItemForm(for_list=mylist, data={"text": "hi"})
        new_item = form.save()
        self.assertEqual(new_item, Item.objects.all()[0])


class NewListTest(TestCase):
    def test_can_save_a_post_request(self):
        self.client.post("/lists/new", data={"text": "A new list item"})
        self.assertEqual(Item.objects.count(), 1)
        new_item = Item.objects.first()
        self.assertEqual(new_item.text, "A new list item")

    def test_redirects_after_post(self):
        response = self.client.post("/lists/new", data={"text": "A new list item"})
        new_list = List.objects.get()
        self.assertRedirects(response, f"/lists/{new_list.id}/")

    def test_validation_errors_are_sent_back_to_home_page_template(self):
        response = self.client.post("/lists/new", data={"text": ""})
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "home.html")
        self.assertIsInstance(response.context["form"], ItemForm)
        self.assertContains(response, escape(EMPTY_ITEM_ERROR))

    def test_invalid_list_items_arent_saved(self):
        self.client.post("/lists/new", data={"text": ""})
        self.assertEqual(List.objects.count(), 0)
        self.assertEqual(Item.objects.count(), 0)


class MyListsTest(TestCase):
    def test_my_lists_url_renders_my_lists_template(self):
        User.objects.create(email="a@b.com")
        response = self.client.get("/lists/users/a@b.com/")
        self.assertTemplateUsed(response, "my_lists.html")

    def test_passes_correct_owner_to_template(self):
        User.objects.create(email="wrong@owner.com")
        correct_user = User.objects.create(email="a@b.com")
        response = self.client.get("/lists/users/a@b.com/")
        self.assertEqual(response.context["owner"], correct_user)

    def test_list_owner_is_saved_if_user_is_authenticated(self):
        user = User.objects.create(email="a@b.com")
        self.client.force_login(user)
        self.client.post("/lists/new", data={"text": "new item"})
        new_list = List.objects.get()
        self.assertEqual(new_list.owner, user)

class ShareListTest(TestCase):
    def test_post_redirects_to_lists_page(self):
        friend = User.objects.create(email="myfriend@example.com")
        mylist = List.objects.create()
        response = self.client.post(
            f"/lists/{mylist.id}/share",
            data={"sharee": "myfriend@example.com"},
        )
        self.assertRedirects(response, mylist.get_absolute_url())

    def test_check_user_added_to_shared_with_attribute(self):
        user = User.objects.create(email="a@b.com")
        friend = User.objects.create(email="myfriend@example.com")
        mylist = List.objects.create(owner=user)
        self.client.post(
            f"/lists/{mylist.id}/share",
            data={"sharee": "myfriend@example.com"}
        )
        self.assertIn(friend, mylist.shared_with.all())
