from django.shortcuts import render , redirect
from groq import Groq
from dotenv import load_dotenv
import os
from django.contrib.auth.forms import UserCreationForm 
from tutor.form import UserForms
from django.contrib.auth.decorators import login_required
from tutor.models import UserProfile

load_dotenv()
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

SYSTEM_PROMOT = "You teach C++ to the students of Pakistan , but you Never give them ans , NEVER write corrected code, even if asked directly.Tell it to ask ONE guiding question at a time, not dump a list of hints at once.You are encouraging, patient, not condescending, Use very simple English — short sentences, no complex vocabulary. Many students speak English as a second language. Avoid words like 'considering,' 'approach,' 'directly' — use plain, everyday words instead.When the student correctly understands and fixes one bug, pause and ask if they want to continue to the next issue or stop here — don't automatically move to the next topic. If the code given is correct tell them it's good and stop"

@login_required
def index(request):
    messages = request.session.get("messages")


    if messages is None:
        messages = [
            {"role" : "system" , "content" : SYSTEM_PROMOT }
        ]

    if request.method == "POST":
        user_code = request.POST.get("code")
        
        messages.append({"role" : "user" , "content" : user_code})
        try:
            response = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=messages
            )
            reply = response.choices[0].message.content

        except Exception as e:
            reply = "Ustadji is having trouble right now. Please try again in a moment."

        messages.append({"role" : "assistant" , "content" : reply})
        
        request.session["messages"] = messages
        
        return render(request, "tutor/index.html", {"messages": messages}) 
    return render(request, "tutor/index.html", {
        "messages": messages
    })

def signup(request):
    if request.method == "POST":
        form = UserForms(request.POST)
        if form.is_valid():
            user = form.save()
            UserProfile.objects.create(user = user)
            return redirect('login')
    else:
        form = UserForms()
    return render(request, 'tutor/signup.html', {'form': form})