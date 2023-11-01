from django.shortcuts import render
import pprint
import google.generativeai as palm
import random
import io
import base64
from PIL import Image
from django.template.defaulttags import register



@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)

def index(request):
    if request.method == "POST":

        gender = request.POST['gender']
        color = request.POST['color']
        power = request.POST['element']

        palm.configure(api_key='AIzaSyDGKPlCQc2tqwNFgdv9oHpgEJfaeMvJoWI')
        models = [m for m in palm.list_models() if 'generateText' in m.supported_generation_methods]
        model = models[0].name
        
        prompt = "Generate 5 unique, orignal, creative, single-word, power ranger attacks that are inspired by "+power+" ,give me output as a simple list without any styling"
        completion = palm.generate_text(
            model=model,
            prompt=prompt,
            temperature=1,
            max_output_tokens=800)

        responce = completion.result
        attack_names = responce.split('\n')
        attacks = []
        images = {}
        img_list = {}
        for attack in attack_names:
            attack_without_number = attack[3:]
            attacks.append(attack_without_number)

        attacks_info = {}
        for i in attacks:
            prompt = "give me single lined info about "+i+" attack"
            completion = palm.generate_text(
                model = model,
                prompt = prompt,
                temperature=1,
                max_output_tokens=800
            )
            attacks_info[i] = completion.result

            prompt = "text to image prompt of the "+color+" Ranger "+gender+" performing the "+i+" attack"
            completion = palm.generate_text(
                model = model,
                prompt = prompt,
                temperature=1,
                max_output_tokens=800
            )
            import requests

            API_URL = "https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-xl-base-1.0"
            headers = {"Authorization": f"Bearer {'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'}"}

            print(completion.result)
            prompt = completion.result
            def query(payload):
                response = requests.post(API_URL, headers=headers, json=payload)
                return response.content
            image_bytes = query({
                "inputs": prompt,
                "guidance_scale": 7.5,
                "num_inference_steps": 200,
                "denoising_strength": 0.8,
            })

            img_list[i] = base64.b64encode(io.BytesIO(image_bytes).getvalue()).decode('utf-8')

        
        data = {
            'attack' : attacks_info,
            'images':images,
            'img_list' : img_list
        }

        return render(request, 'index.html', data)

    return render(request, 'index.html')
