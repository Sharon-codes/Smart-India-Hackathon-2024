import torch
from transformers import LlamaTokenizer, LlamaForCausalLM
from diffusers import StableDiffusionPipeline
from PIL import Image
import numpy as np
import cv2
import io

# Initialize LLaMA model and tokenizer
llama_model_name = 'meta-llama/Llama-7b-hf'  # Replace with the actual LLaMA model
tokenizer = LlamaTokenizer.from_pretrained(llama_model_name)
model = LlamaForCausalLM.from_pretrained(llama_model_name)

# Initialize Stable Diffusion pipeline
pipe = StableDiffusionPipeline.from_pretrained("CompVis/stable-diffusion-v1-4")

def generate_description(prompt):
    inputs = tokenizer(prompt, return_tensors='pt')
    outputs = model.generate(**inputs, max_length=50)
    description = tokenizer.decode(outputs[0], skip_special_tokens=True)
    return description

def generate_image_from_text(description):
    # Generate image using Stable Diffusion
    image = pipe(description).images[0]
    return image

def create_video_from_images(images, output_file='output_video.mp4'):
    frame_size = images[0].size
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(output_file, fourcc, 1.0, frame_size)

    for img in images:
        frame = np.array(img)
        frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)  # Convert RGB to BGR
        out.write(frame)

    out.release()

def main():
    prompt = "A serene landscape with mountains and a river"

    # Generate description
    description = generate_description(prompt)
    print("Generated Description:", description)
    
    # Generate images from description
    images = [generate_image_from_text(description) for _ in range(10)]  # Generate 10 frames

    # Create video from images
    create_video_from_images(images)

    print("Video created successfully!")

if __name__ == '__main__':
    main()
