# Inventory and Clock-In System

This FastAPI application provides a simple inventory management and clock-in system with CRUD operations for items and user clock-in records.


## Prerequisites

- Python 3.8+
- MongoDB (local instance or MongoDB Atlas)

## Installation

1. Clone the repository:

2. Create a virtual environment and activate it:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```

3. Install the required packages:
   ```
   pip install -r requirements.txt
   ```

4. Create a `.env` file in the project root and add your MongoDB connection string:
   ```
   MONGO_URL=your_mongodb_connection_string_here
   ```

## Running Locally

To run the application locally:

1. Ensure you're in the project directory with the virtual environment activated.

2. Start the FastAPI server:
   ```
   uvicorn main:app --reload
   ```

3. Open your browser and navigate to `http://localhost:8000/docs` to view the Swagger UI documentation and interact with the API.

## API Documentation

Once the application is running, you can access the full API documentation at:

- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Deployment

This application is deployed on Koyeb. You can access the live version at:

https://constant-clemmie-vodex-2f969be8.koyeb.app/docs

https://constant-clemmie-vodex-2f969be8.koyeb.app/redoc
