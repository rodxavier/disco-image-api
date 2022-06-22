# disco-image-api

Disco Technical Test

This repo contains a simple DRF-based image API

## Setup

1. Run `docker compose up`
2. Visit `http://localhost:8000`

`Note`: An admin account was already created with the credentials `admin/password`.

## Running test

`docker compose run "python manage.py test"`

## Creating a new Plan

1. Visit the django admin. `http://localhost:8000/admin`
2. Go to the Plan admin page

   ![Plan Admin](misc/plan_admin.png?raw=true "Plan admin")

3. Assign a name to the new Plan
4. Choose available presets or create a new one

   ![Image Preset](misc/image_preset.png?raw=true "Image preset")

5. Save the new Plan

## FAQs

1. What is an ImagePreset?

The ImagePreset model represents a size configuration for an image. You can define the height and/or width of the preset. The following scenarios are handled:

- If no height and width values, the preset will do nothing but return the original image
- If height and width are present, the preset will resize the image to the specific dimensions
- If either height or width is present, the preset will resize the image to the specific dimension present while maintaining the aspect ratio of the image

## TODOs

- Implement caching mechanism in ImageUrlView
