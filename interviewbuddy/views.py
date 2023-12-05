from .forms import LoginForm, RegisterForm
from django.views.generic.edit import FormView
from django.contrib import messages
from interviewbuddy.config import Config
from pymongo import MongoClient
from django.shortcuts import render
from .database import Database
from .config import Config
from django.contrib.auth.decorators import login_required, permission_required
from django.shortcuts import redirect
import openai, os
from .config import OpenaiKey
from django.views.decorators.csrf import csrf_exempt


api_key = OpenaiKey.key
# Create your views here.
client = MongoClient(Config.DB_CONNECTION)
dbname = client['test_database']
# Send a ping to confirm a successful connection
try:
    client.admin.command('ping')
    print("Pinged your deployment. You successfully connected to MongoDB!")
except Exception as e:
    print(e)

db = Database()
class UserInfo:
    def __init__(self):
        self.uid = None
        self.password = None



logged_user = UserInfo()

def home_view(request):
    return render(request, 'home.html')

@csrf_exempt  # CSRF exemption for simplicity;
def chat_view(request):
    chatbot_response = None
    prompt = {"role": "user", "content": ""}
    chat_list = []

    if db.check_username(logged_user.uid):

        data = db.get_all_data_from_collection(logged_user.uid)
        for item in data:
            chat_list.append(item)

        if api_key is not None:
            if request.method == 'POST':
                openai.api_key = api_key
                user_input = request.POST.get('user_input')
                log = {"role": "user", "content": user_input}
                chat_list.append(log)

                response = openai.ChatCompletion.create(
                    model="gpt-3.5-turbo",
                    messages = chat_list
                )
                chatbot_response = response['choices'][0]['message']['content']

                db.add_chat_log_to_user_collection(logged_user.uid, log)
                db.add_chat_log_to_user_collection(logged_user.uid, {"role": "assistant", "content": chatbot_response})
        return render(request, 'chat.html', {'user_input': prompt, 'chatbot_response': chatbot_response})
    else:
        return render(request, 'home.html')

class LoginView(FormView):
    template_name = 'registration/login.html'
    form_class = LoginForm
    success_url = '/home'  # Redirect to this URL on successful form submission

    def login_user(self, username, password):
        # Your custom login logic here
        # This could involve checking credentials, setting session variables, etc.
        pass

    def form_valid(self, form):
        # Call your custom function

        # You can also access form data using form.cleaned_data
        username = form.cleaned_data['username']
        password = form.cleaned_data['password']

        # Add your authentication logic here (e.g., check credentials)
        print(username,password)
        response = db.login_user(username, password)
        print(response)
        if "successful" in response:
            logged_user.uid = username
            logged_user.password = password
            return redirect('chat')
        else:
            messages.error(self.request, response)

        return super().form_invalid(form)

    def form_invalid(self, form):
        # Your form validation failed, handle it here
        # You might want to add a message to inform the user about the error
        messages.error(self.request, 'Invalid login credentials. Please try again.')

        # Redirect to the login page or any other appropriate URL
        return super().form_invalid(form)


class RegisterView(FormView):
    template_name = 'registration/register.html'
    form_class = RegisterForm  # Create a RegisterForm similar to the LoginForm
    success_url = '/accounts/login'  # Redirect to this URL on successful form submission

    def form_valid(self, form):
        # Get the registration form data
        username = form.cleaned_data['username']
        password = form.cleaned_data['password']
        confirm_password = form.cleaned_data['confirm_password']

        # Add your registration logic using the Database class here
        result_message = db.register_user(username, password)

        # Add a success or error message based on the result
        if "successful" in result_message:
            messages.success(self.request, result_message)
            return super().form_valid(form)
        else:
            messages.error(self.request, result_message)

        # If registration is unsuccessful, do not redirect to the success URL
        return super().form_invalid(form)

    def form_invalid(self, form):
        # Your form validation failed, handle it here
        # You might want to add a message to inform the user about the error

        # Redirect to the login page or any other appropriate URL
        return super().form_invalid(form)
