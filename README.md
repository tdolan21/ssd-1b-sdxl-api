# SSD-1B Interface

![SSD-1B Header Image](assets/SSD_1B.png)


Here is the model description from the Segmind AI team: 

The Segmind Stable Diffusion Model (SSD-1B) is a distilled 50% smaller version of the Stable Diffusion XL (SDXL), offering a 60% speedup while maintaining high-quality text-to-image generation capabilities. It has been trained on diverse datasets, including Grit and Midjourney scrape data, to enhance its ability to create a wide range of visual content based on textual prompts.

More information can be found [here](https://huggingface.co/segmind/SSD-1B).

## Prerequisites

SSD-1B Interface requires at least PostgreSQL 14.

SSD-1B Interface requires the dev version of  diffusers. Make sure to include this step of the installation.

## Installation

```bash
<<<<<<< HEAD
git clone https://github.com/tdolan21/ssd-8b-ui
=======
git clone https://github.com/tdolan21/ssd-1b-ui
>>>>>>> 322c66b3214aaab149ee7f83e12d5f3c1d206e48
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

**/generate-image**: Generate an image using a prompt and a negative prompt.
**/image-records**: Returns the 5 most recent image entries including prompt details.


## License

This project is licensed with Apache 2.0

