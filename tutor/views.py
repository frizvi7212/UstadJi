from django.shortcuts import render, redirect
from groq import Groq
from dotenv import load_dotenv
import os
from django.contrib.auth.forms import UserCreationForm
from tutor.form import UserForms
from django.contrib.auth.decorators import login_required
from tutor.models import UserProfile, Conversation, Message
from django.utils import timezone
from datetime import timedelta

load_dotenv()
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
SYSTEM_PROMOT = "You teach C++ to beginner students in Pakistan. Never give the answer or corrected code, even if asked directly. Ask one simple guiding question at a time — no long hint lists. Use short sentences and plain English, since many students are ESL. Be warm and patient, never condescending. When a bug is fixed, ask if they want to continue or stop — don't move on automatically. If the code is already correct, say so and stop."

@login_required
def index(request):
    latest_convo = Conversation.objects.filter(user=request.user).order_by('-created_at').first()

    if latest_convo is None:
        latest_convo = Conversation.objects.create(user=request.user)
        Message.objects.create(conversation=latest_convo, role="system", content=SYSTEM_PROMOT)

    profile = UserProfile.objects.get(user= request.user)
    elapsed = timezone.now() - profile.trial_start
    trial_ended = elapsed >= timedelta(days=15) or profile.message_count >= 100
    if request.method == "POST":
        if trial_ended:
             messages = Message.objects.filter(conversation=latest_convo)
             return render(request, "tutor/index.html", {"messages": messages, "trial_ended": True})
        else:
            user_code = request.POST.get("code")
            Message.objects.create(conversation=latest_convo, role="user", content=user_code)

            profile.message_count +=1
            profile.save()
            # build trimmed message history for Groq (system prompt + last 20 messages)
            recent_messages = list(Message.objects.filter(conversation=latest_convo).exclude(role="system").order_by('-timestamp')[:20])
            recent_messages.reverse()
            messages = [{"role": "system", "content": SYSTEM_PROMOT}]
            for msg in recent_messages:
                messages.append({"role": msg.role, "content": msg.content})


                # handles error if token finishes
            try:
                print(len(messages))
                response = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=messages,
                max_tokens=300
                )
                reply = response.choices[0].message.content
            except Exception as e:
                reply = "Ustadji is having trouble right now. Please try again in a moment."

            Message.objects.create(conversation=latest_convo, role="assistant", content=reply)

            messages = Message.objects.filter(conversation=latest_convo)
            return render(request, "tutor/index.html", {"messages": messages})
    #exexutes when it's not a post request
    messages = Message.objects.filter(conversation=latest_convo)
    return render(request, "tutor/index.html", {"messages": messages})


def signup(request):
    if request.method == "POST":
        form = UserForms(request.POST)
        if form.is_valid():
            user = form.save()
            UserProfile.objects.create(user=user)
            return redirect('login')
    else:
        form = UserForms()
    return render(request, 'tutor/signup.html', {'form': form})