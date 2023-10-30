from sqlalchemy import create_engine, Column, Integer, String, DateTime, func, select
from sqlalchemy.ext.declarative import declarative_base
from fastapi import FastAPI, Depends, HTTPException, Body
from starlette.responses import StreamingResponse
from diffusers import StableDiffusionXLPipeline
from fastapi.responses import FileResponse
from sqlalchemy.orm import sessionmaker
from diffusers import DiffusionPipeline
from pydantic import BaseModel
from sqlalchemy import desc
from typing import List
from PIL import Image
import sqlalchemy
import databases
import base64
import torch
import time
import uuid
import io
import os


print("Setting database configuration..")
DATABASE_URL = "postgresql://postgres:postgres@localhost:5432/ssd_1b"

database = databases.Database(DATABASE_URL)
metadata = sqlalchemy.MetaData()

Base = declarative_base()

app = FastAPI()

# Initialize the model once for efficiency
sdxl_pipe = DiffusionPipeline.from_pretrained(
    "stabilityai/stable-diffusion-xl-base-1.0",
    torch_dtype=torch.float16,
    use_safetensors=True,
    variant="fp16"
)


pipe = StableDiffusionXLPipeline.from_pretrained(
    "segmind/SSD-1B", 
    torch_dtype=torch.float16, 
    use_safetensors=True, 
    variant="fp16"
)
sdxl_pipe.to("cuda:0")
pipe.to("cuda:0")

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

class ImageRecordCreate(BaseModel):
    prompt: str
    negative_prompt: str
    image_path: str

class  SDXLImageRecord(Base):
    __tablename__ = "sdxl_images"

    id = Column(Integer, primary_key=True, index=True)
    prompt = Column(String, index=True)
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

#===================================================================================================
############### SDXL ENDPOINTS ###############
#===================================================================================================

@app.post("/sdxl-gen/")
async def generate_image(prompt: str = Body(...)):
    start_time = time.time()
    print("Received image generation request...")
    try:
        # Generate image
        print("Generating image using the provided prompt...")
        image = sdxl_pipe(prompt=prompt).images[0]

        # Generate a unique UUID and use it for the filename
        unique_id = str(uuid.uuid4())
        print(f"Generated UUID: {unique_id}")

        # Save the image to the folder
        print("Saving generated image locally...")
        image_path = os.path.join('generated_images', f"{unique_id}.jpg")
        image.save(image_path, format="JPEG")

        # Save image details to database
        print("Saving image details to database...")
        record = SDXLImageRecord(prompt=prompt, image_path=image_path)

        # Create an insert query
        query = SDXLImageRecord.__table__.insert().values(
            prompt=record.prompt,
            image_path=record.image_path
        )

        # Execute the insert query
        async with database.transaction():
            await database.execute(query)

        end_time = time.time()  # End the timer
        generation_time = end_time - start_time  # Calculate time taken

        # Convert image to bytes for streaming
        buffer = io.BytesIO()
        image.save(buffer, format="JPEG")
        image_base64 = base64.b64encode(buffer.getvalue()).decode()

        buffer.seek(0)

        print("Returning generated image...")
        return {
        "image": image_base64,
        "generation_time": generation_time
    }

    except Exception as e:
        print(f"Error occurred: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


##/GET ENDPOINTS TO FETCH SDXL RECORDS
@app.get("/sdxl-records/")
async def get_sdxl_records():
    try:
        # Fetch the 5 most recent records from the database
        query = SDXLImageRecord.__table__.select().order_by(desc(SDXLImageRecord.timestamp)).limit(5)
        records = await database.fetch_all(query)
        
        # Convert records to a list of dictionaries
        result = [dict(record) for record in records]
        
        return result
    except Exception as e:
        print(f"Error fetching records: {str(e)}")
        raise HTTPException(status_code=500, detail="Error fetching records from the database.")



#===================================================================================================
############### SSD-1B /POST ENDPOINTS ###############
#===================================================================================================


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

# Clear database from the application
@app.post("/clear-database/")
async def clear_database():
    try:
        query = ImageRecord.__table__.delete()
        await database.execute(query)
        return {"status": "success", "message": "Database cleared successfully!"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/import-records/")
async def import_records(records: List[ImageRecordCreate]):
    try:
        query = ImageRecord.__table__.insert()
        await database.execute_many(query, records)
        return {"status": "success", "message": "History imported successfully!"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    


#===================================================================================================
############### /GET ENDPOINT TO FETCH ALL RECORDS ###############
#===================================================================================================


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

# Endpoint to fetch all records from both SSD-1B and SDXL
@app.get("/all-records/")
async def get_all_image_records():
    try:
        # Fetch all records from the ImageRecord table
        query_image_records = ImageRecord.__table__.select().order_by(desc(ImageRecord.timestamp))
        image_records = await database.fetch_all(query_image_records)

        # Fetch all records from the SDXLImageRecord table
        query_sdxl_records = SDXLImageRecord.__table__.select().order_by(desc(SDXLImageRecord.timestamp))
        sdxl_records = await database.fetch_all(query_sdxl_records)
        
        # Convert ImageRecord entries to a list of dictionaries
        image_result = [dict(record) for record in image_records]

        # Convert SDXLImageRecord entries to a list of dictionaries and add a default value for negative_prompt
        sdxl_result = [{"id": record["id"], "prompt": record["prompt"], "negative_prompt": None, "image_path": record["image_path"], "timestamp": record["timestamp"]} for record in sdxl_records]

        # Combine the results
        combined_result = image_result + sdxl_result
        
        # Sort combined records by timestamp
        sorted_result = sorted(combined_result, key=lambda x: x["timestamp"], reverse=True)
        
        return sorted_result
    except Exception as e:
        print(f"Error fetching records: {str(e)}")
        raise HTTPException(status_code=500, detail="Error fetching records from the database.")


# Endpoint to fetch high-level statistics about the database
@app.get("/database-info/")
async def get_database_info():
    # Fetch total number of records for ImageRecord (SSD 1B)
    total_image_records_query = select([func.count()]).select_from(ImageRecord.__table__)
    total_image_records = await database.fetch_val(total_image_records_query)

    # Fetch total number of records for SDXLImageRecord
    total_sdxl_records_query = select([func.count()]).select_from(SDXLImageRecord.__table__)
    total_sdxl_records = await database.fetch_val(total_sdxl_records_query)

    return {
        "database_name": "ssd_1b",  # Replace with your actual database name
        "ssd_1b_records": total_image_records,
        "sdxl_records": total_sdxl_records,
    }

if __name__ == "__main__":
    print("Creating database tables if not present...")
    Base.metadata.create_all(bind=engine)
    print("Starting FastAPI application...")
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

