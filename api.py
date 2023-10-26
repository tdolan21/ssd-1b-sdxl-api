from sqlalchemy import create_engine, Column, Integer, String, DateTime, func
from sqlalchemy.ext.declarative import declarative_base
from diffusers import StableDiffusionXLPipeline
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.orm import sessionmaker
from pydantic import BaseModel
from sqlalchemy import desc
import sqlalchemy
import databases
import torch
import uuid

print("Setting database configuration..")
DATABASE_URL = "postgresql://postgres:postgres@localhost:5432/ssd_1b"

database = databases.Database(DATABASE_URL)
metadata = sqlalchemy.MetaData()

Base = declarative_base()

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

# Image request model
class ImageRequest(BaseModel):
    prompt: str
    negative_prompt: str

# Image record model
class ImageRecord(Base):
    __tablename__ = "images"

    id = Column(Integer, primary_key=True, index=True)
    prompt = Column(String, index=True)
    negative_prompt = Column(String, index=True)
    image_path = Column(String)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())

# Create database engine and session
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)

# Connect to database on application startup
@app.on_event("startup")
async def startup():
    print("Connecting to PostgreSQL...")
    await database.connect()

# Shutdown database on application close
@app.on_event("shutdown")
async def shutdown():
    print("Shutting down PostgreSQL...")
    await database.disconnect()

# Generate an image, and store the details in the database
@app.post("/generate-image/")
async def generate_image(request: ImageRequest):
    print("Received image generation request...")
    try:
        print("Generating image using the provided prompts...")
        image = pipe(prompt=request.prompt, negative_prompt=request.negative_prompt).images[0]

        # Generate a unique UUID and use it for the filename
        unique_id = str(uuid.uuid4())
        print(f"Generated UUID: {unique_id}")

        print("Saving generated image locally...")
        image_path = f"generated_images/{unique_id}.jpg"
        image.save(image_path)
        
        print("Saving image details to database...")
        # Save data to the database
        record = ImageRecord(prompt=request.prompt, negative_prompt=request.negative_prompt, image_path=image_path)

        # Create an insert query
        query = ImageRecord.__table__.insert().values(
            prompt=record.prompt, 
            negative_prompt=record.negative_prompt, 
            image_path=record.image_path
        )

        # Execute the insert query
        async with database.transaction():
            await database.execute(query)
        
        print("Returning generated image...")
        return FileResponse(image_path, media_type="image/jpg")

    except Exception as e:
        print(f"Error occurred: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

## Endpoint to fetch the 5 most recent records
@app.get("/image-records/")
async def get_image_records():
    try:
        # Fetch the 5 most recent records from the database
        query = ImageRecord.__table__.select().order_by(desc(ImageRecord.timestamp)).limit(5)
        records = await database.fetch_all(query)
        
        # Convert records to a list of dictionaries
        result = [dict(record) for record in records]
        
        return result
    except Exception as e:
        print(f"Error fetching records: {str(e)}")
        raise HTTPException(status_code=500, detail="Error fetching records from the database.")

## New endpoint to fetch all records
@app.get("/all-records/")
async def get_all_image_records():
    try:
        # Fetch all records from the database
        query = ImageRecord.__table__.select().order_by(desc(ImageRecord.timestamp))
        records = await database.fetch_all(query)
        
        # Convert records to a list of dictionaries
        result = [dict(record) for record in records]
        
        return result
    except Exception as e:
        print(f"Error fetching records: {str(e)}")
        raise HTTPException(status_code=500, detail="Error fetching records from the database.")

if __name__ == "__main__":
    print("Creating database tables if not present...")
    Base.metadata.create_all(bind=engine)
    print("Starting FastAPI application...")
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)


