# SSD-1B Interface

![Python](https://img.shields.io/badge/Python-3.8%2B-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-0.68.0-green)
![Streamlit](https://img.shields.io/badge/Streamlit-1.0.0-red)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-14-orange)
![Diffusers](https://img.shields.io/badge/Diffusers-dev-yellowgreen)



![SSD-1B Header Image](assets/SSD_1B.png)


Here is the model description from the Segmind AI team: 

The Segmind Stable Diffusion Model (SSD-1B) is a distilled 50% smaller version of the Stable Diffusion XL (SDXL), offering a 60% speedup while maintaining high-quality text-to-image generation capabilities. It has been trained on diverse datasets, including Grit and Midjourney scrape data, to enhance its ability to create a wide range of visual content based on textual prompts.

More information can be found [here](https://huggingface.co/segmind/SSD-1B).

## Prerequisites

SSD-1B Interface requires at least PostgreSQL 14.

SSD-1B Interface requires the dev version of  diffusers. Make sure to include this step of the installation.

## Installation

```bash
git clone https://github.com/tdolan21/ssd-8b-ui
cd SSD-1B-UI
pip install -r requirements.txt
cd db-init
python init.py
cd ..
```

```bash
pip install git+https://github.com/huggingface/diffusers
```

## Usage

Linux:

```bash
chmod +x run.sh
./run.sh
```

Windows: 

```bash
run.bat
```

After running the startup script the UI will be available at:

```
127.0.0.1:8501
```

The API will be available at:

```
127.0.0.1:8000/docs
```

## Endpoints

- **/generate-image** (POST): Generate an image using a prompt and a negative prompt. The details of the generated image (prompt, negative prompt, and image path) are stored in the database, and the generated image is returned as a response.
- **/image-records** (GET): Fetch the 5 most recent image generation records, including the prompts used and the path to the generated image.
- **/all-records** (GET): Retrieve all image generation records in the database, sorted by their creation timestamps in descending order.
- **/clear-database** (POST): Clear all records from the database. This action removes all image generation records.
- **/import-records** (POST): Import a list of image generation records into the database. This is useful for restoring a previously exported history.
- **/database-info** (GET): Get statistics about the database, such as the total number of image generation records stored.

## License

This project is licensed with Apache 2.0

