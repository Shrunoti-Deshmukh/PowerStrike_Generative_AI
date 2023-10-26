from django.shortcuts import render
import pprint
import google.generativeai as palm
import random
import io
import base64
from PIL import Image
import cv2

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
        img_list = []
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
            print(completion.result)
            import requests

            API_URL = "https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-xl-base-1.0"
            headers = {"Authorization": f"Bearer {'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'}"}

            prompt = "The Pink Ranger's power stone is an exquisite gem, imbued with the essence of love and courage. Its delicate shade of soft pink reflects her unwavering determination and compassion. When harnessed, it grants her the ability to conjure protective barriers and healing energy, embodying the enduring power of love in the face of darkness."
            def query(payload):
                response = requests.post(API_URL, headers=headers, json=payload)
                return response.content
            image_bytes = query({
                "inputs": prompt,
                "guidance_scale": 7.5,
                "num_inference_steps": 200,
                "denoising_strength": 0.8,
            }).decode('latin-1')
            
            # image = Image.open(io.BytesIO(image_bytes))
            # # Upscale the image to 512x512 pixels
            # image = image.resize((1024, 1024))
            
            # name = i+".jpg"
            # print(type(image))

            # with io.BytesIO() as buffer:
            #     image.save(buffer,format="JPEG")
            #     image_bytes = buffer.getvalue()

            # img_list = Image.frombytes("L",(3,2),image_bytes)
            # img_list = base64.b64decode(image_bytes).decode('latin-1')

            print(img_list)
        
        data = {
            'attack' : attacks_info,
            'images':images,
            'img_list' : image_bytes
        }
        return render(request, 'index.html', data)

    return render(request, 'index.html')
