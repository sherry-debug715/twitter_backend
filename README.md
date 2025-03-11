# Twitter Backend Project

## Overview
This project is a backend implementation for a Twitter-like application. It is containerized using Docker, enabling easy setup and deployment in a virtual environment. The backend handles user accounts, tweets, and other core functionalities.

---

## Prerequisites
1. Install [Docker](https://www.docker.com/) and ensure Docker Compose is installed.
2. Clone the repository:
   ```bash
   git clone git@github.com:sherry-debug715/twitter_backend.git
   cd twitter_backend
   ```
3. Python 3.8+ is required only for local development outside Docker. If you're using Docker, Python installation on your host system is not necessary.

---

## Setup Instructions

### Using Docker
Build and run the Docker containers. Make sure you are in the same directory as the docker-compose.yaml file and Dockerfile:

Using the Makefile, we can manage tasks easily:

- Build a Docker image:
  ```bash
  make build
  ```
- Start and run all services:
  ```bash
  make up
  ```
- Enter twitter container shell:
  ```bash
  make enter
  ```
- Please stay in the twitter shell to run the first migration to set up the databse schema:
    ```bash
    python manage.py migrate
    ```
- (Optional) Create a Superuser for admin access
    ```bash
    python manage.py createsuperuser
    ```
- Exit twitter container shell using :
    - Type exit and press Enter 
    ```bash
    exit
    ```
    - Press Ctrl + D simultaneously
- See Docker logs
    ```bash
    make logs
    ```
- Access the application on `http://localhost:8000` (default). Ensure no port conflicts with other running services.

- Stop the Docker image:
  ```bash
  make stop
  ```
---

## Testing
Run tests inside the Docker container:

- Make sure all Docker containers are running, if not, use:
    ```bash
    make build && make up && make logs
    ```
- Enter twitter container shell:
  ```bash
  make enter
  ```
- Inside the twitter container shell:
    ```bash
    python manage.py test -v2
    ```
---

```python
    # Custom display functions: show associated file name on each row, if any.
    def display_linked_file(self, obj):
        def formatFileName(file_name):
            if not len(file_name) > 1:
                return ""
            email_filename = file_name.split(" - ")
            if not len(email_filename) > 1:
                return ""
            file_name = email_filename[1].split("_")
            formated_fileName = ""
            for i in range(1, len(file_name)):
                formated_fileName += file_name[i] + "_"
            return formated_fileName[:-1]
   
        linked_files = []
        # Check the forward relationship first.
        if hasattr(obj, 'linked_video_file'):
            attr = obj.linked_video_file
            if callable(getattr(attr, "all", None)):
                qs = attr.all() 
                if qs.exists():
                    linked_files.extend(qs)
            elif attr: # If there is only one linked file
                linked_files.append(attr) 
        # Otherwise, try the reverse relationship.
        if not linked_files and hasattr(obj, 'linked_media'):
            attr = obj.linked_media
            if callable(getattr(attr, "all", None)):
                qs = attr.all() 
                if qs.exists():
                    linked_files.extend(qs)
            elif attr: # If there is only one linked file
                linked_files.append(attr)
        
        formatted_names = [formatFileName(str(file)) for file in linked_files if formatFileName(str(file))]

        return format_html('<br>'.join(formatted_names)) if formatted_names else "-"

    display_linked_file.short_description = "Linked File Name"
```

