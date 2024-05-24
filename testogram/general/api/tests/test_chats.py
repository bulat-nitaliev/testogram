import time
from rest_framework.test import APITestCase
from rest_framework import status
from general.factories import  UserFactory,  ChatFactory, MessageFactory
from general.models import Chat,  Message   
from django.utils.timezone import make_naive

class ChatTestCase(APITestCase):
    def setUp(self):
        self.user = UserFactory()
        self.client.force_authenticate(user=self.user)
        self.url = "/api/chats/"
        print(self)

    def test_get_chat_list(self):
        user_1 = UserFactory()
        user_2 = UserFactory()
        user_3 = UserFactory()

        chat_1 = ChatFactory(user_1=self.user, user_2=user_1)
        chat_2 = ChatFactory(user_1=self.user, user_2=user_2)
        chat_3 = ChatFactory(user_1=user_3, user_2=self.user)

        mes_1 = MessageFactory(author=self.user, chat=chat_1)
        time.sleep(1)
        mes_3 = MessageFactory(author=self.user, chat=chat_3)
        time.sleep(1)
        mes_2 = MessageFactory(author=user_2, chat=chat_2)

        MessageFactory.create_batch(10)

        with self.assertNumQueries(2):
            response = self.client.get(self.url, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # чаты сортируются по дате последнего сообщения.
        # поэтому порядок чатов должен быть такой: chat_2, chat_3, chat_1.
        # создаем список ID чатов из response.
        response_chat_ids = [chat["id"] for chat in response.data["results"]]
        # response_chat_ids = [response.data["results"][0]["id"],response.data["results"][1]["id"],response.data["results"][2]["id"]]
        expected_chat_ids = [chat_2.pk, chat_3.pk, chat_1.pk]
        self.assertListEqual(response_chat_ids, expected_chat_ids)
        # теперь проверяем каждый отдельный чат.
        chat_2_expected_data = {
            "id": chat_2.pk,
            "companion_name": f"{user_2.first_name} {user_2.last_name}",
            "last_message_content": mes_2.content,
            "last_message_datetime": make_naive(mes_2.created_at).strftime("%Y-%m-%dT%H:%M:%S"),
        }
        self.assertDictEqual(response.data["results"][0], chat_2_expected_data)

        chat_3_expected_data = {
            "id": chat_3.pk,
            "companion_name": f"{user_3.first_name} {user_3.last_name}",
            "last_message_content": mes_3.content,
            "last_message_datetime": make_naive(mes_3.created_at).strftime("%Y-%m-%dT%H:%M:%S"),
        }
        self.assertDictEqual(response.data["results"][1], chat_3_expected_data)

        chat_1_expected_data = {
            "id": chat_1.pk,
            "companion_name": f"{user_1.first_name} {user_1.last_name}",
            "last_message_content": mes_1.content,
            "last_message_datetime": make_naive(mes_1.created_at).strftime("%Y-%m-%dT%H:%M:%S"),
        }
        self.assertDictEqual(response.data["results"][2], chat_1_expected_data)

    def test_create_chat(self):
        user = UserFactory()
        data = {"user_2": user.pk}
        response = self.client.post(self.url, data=data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        chat = Chat.objects.last()
        self.assertEqual(chat.user_1, self.user)
        self.assertEqual(chat.user_2, user)

        expected_data = {
            "id": chat.pk,
            "user_2": user.pk
        }
        self.assertDictEqual(response.data, expected_data)

    def test_try_to_create_chat_when_exists(self):
        user = UserFactory()
        chat = ChatFactory(user_1=self.user, user_2=user)
        data = {"user_2": user.pk}
        response = self.client.post(self.url, data=data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        chats = Chat.objects.all()
        self.assertEqual(chats.count(), 1)
        

        expected_data = {
            "id": chat.pk,
            "user_2": user.pk
        }
        self.assertDictEqual(response.data, expected_data)

    def test_try_to_create_chat_when_exists_reversed(self):
        user = UserFactory()
        chat = ChatFactory(user_1=user, user_2=self.user)
        data = {
            "user_2": user.pk
        }
        response = self.client.post(self.url, data=data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        chats = Chat.objects.all()
        self.assertEqual(chats.count(), 1)
        chat = Chat.objects.last()
        self.assertEqual(chat.user_1, user)
        self.assertEqual(chat.user_2, self.user)
        expected_data = {
            "id": chat.pk,
            "user_2": user.pk
        }
        self.assertDictEqual(response.data, expected_data)

    def test_delete_chat(self):
        chat_1 = ChatFactory(user_1=self.user)
        chat_2 = ChatFactory(user_2=self.user)
        mes_1 = MessageFactory(author=self.user, chat=chat_1)
        mes_2 = MessageFactory(author=self.user, chat=chat_2)
        
        response = self.client.delete(f"{self.url}{chat_1.pk}/", format="json")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        response = self.client.delete(f"{self.url}{chat_2.pk}/", format="json")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        self.assertEqual(Chat.objects.all().count(), 0)
        self.assertEqual(Message.objects.all().count(), 0)

    def test_try_to_delete_other_chat(self):
        chat = ChatFactory()
        response = self.client.delete(f"{self.url}{chat.pk}/", format="json")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        self.assertEqual(Chat.objects.all().count(), 1)

    def test_get_messages(self):
        user = UserFactory()
        chat = ChatFactory(user_1=self.user, user_2=user)
        mes_1 = MessageFactory(author=self.user, chat=chat)
        time.sleep(1)
        mes_2 = MessageFactory(author=user, chat=chat)
        time.sleep(1)
        mes_3 = MessageFactory(author=self.user, chat=chat)

        url = f"{self.url}{chat.pk}/messages/"
        with self.assertNumQueries(2):
            response = self.client.get(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 3)

        mes_3_expected_data = {
            "id": mes_3.pk, 
            "content": mes_3.content, 
            "message_author": "Вы", 
            "created_at": make_naive(mes_3.created_at).strftime("%Y-%m-%dT%H:%M:%S")
        }
        self.assertDictEqual(mes_3_expected_data, response.data[0])

        mes_2_expected_data = {
            "id": mes_2.pk, 
            "content": mes_2.content, 
            "message_author": user.first_name, 
            "created_at": make_naive(mes_2.created_at).strftime("%Y-%m-%dT%H:%M:%S")
        }
        self.assertDictEqual(mes_2_expected_data, response.data[1])

        mes_1_expected_data = {
            "id": mes_1.pk, 
            "content": mes_1.content, 
            "message_author": "Вы", 
            "created_at": make_naive(mes_1.created_at).strftime("%Y-%m-%dT%H:%M:%S")
        }
        self.assertDictEqual(mes_1_expected_data, response.data[2])

    def test_get_messages_not_exists(self):
        chat = ChatFactory()
        url = f"{self.url}{chat.pk}/messages/"
        with self.assertNumQueries(1):
            response = self.client.get(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(Chat.objects.all().count(), 1)














        
