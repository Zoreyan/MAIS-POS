from django.shortcuts import render
import requests



def chat(request):
    response = None

    if request.method == 'POST':
        question = request.POST.get('question')
        API_URL = "https://api-inference.huggingface.co/models/google/gemma-2-2b-it"
        headers = {"Authorization": "Bearer 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"}
        payload = {
            "inputs": question,
        }
        response = requests.post(API_URL, headers=headers, json=payload)
    context = {
        'response': response.json()[0]['generated_text'] if response else None
    }
    return render(request, 'ai/chat.html', context)