from fastapi import FastAPI, HTTPException
from diffusers import StableDiffusionXLPipeline
import torch
from fastapi.responses import FileResponse
from pydantic import BaseModel

app = FastAPI()

pipe = StableDiffusionXLPipeline.from_pretrained(
    "segmind/SSD-1B", 
    torch_dtype=torch.float16, 
    use_safetensors=True, 
    variant="fp16"
)
pipe.to("cuda")

# if using torch < 2.0
# pipe.enable_xformers_memory_efficient_attention()

class ImageRequest(BaseModel):
    prompt: str
    negative_prompt: str

@app.post("/generate-image/")
def generate_image(request: ImageRequest):
    try:
        image = pipe(prompt=request.prompt, negative_prompt=request.negative_prompt).images[0]

        # Save the image to the generated_images folder
        image_path = "generated_images/image.png"
        image.save(image_path)

        return FileResponse(image_path, media_type="image/png")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
