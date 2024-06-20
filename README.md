# Test backend task


## Description
This project is a web application built using FastAPI. I create CRUD operations, implemented by my own JWT authorization, with access and refresh tokens using middleware.

## Installation
1. Clone this repository:

    ```bash
    git clone  https://github.com/WorkingHardDev/test_backend.git
    cd test_backend
    ```

2. Create and activate a virtual environment:

    ```bash
    python -m venv venv
    source venv/bin/activate  # For Windows use `venv\Scripts\activate`
    ```

3. Install dependencies from `requirements.txt`:

    ```bash
    pip install -r requirements.txt
    ```

## Running the Project

To run the project, use the following command:

```bash
uvicorn main:app --host 0.0.0.0 --port 8081 --reload

# or you can use Docker 
