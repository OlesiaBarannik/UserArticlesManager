
# User Articles Manager

## Description

User Articles Manager is a simple REST API built with Flask for managing users and their associated articles. The system allows you to add, retrieve, update, and delete users and articles. The data is stored in a PostgreSQL database. This project is containerized using Docker for easy setup and deployment.

---

## Features

### **User Management**
- **POST /login**: Authenticate a user and retrieve a JWT token.
- **GET /api/users**: Retrieve a list of all users (Admin only).
- **GET /api/users/{user_id}**: Retrieve details of a specific user (Admin only).
- **GET /api/users/search**: Search users by username (Admin only).
- **PATCH /api/users/{user_id}**: Update user details (Admin only).
- **DELETE /api/users/{user_id}**: Delete a user and their associated articles (Admin only).

### **Article Management**
- **GET /api/articles**: Retrieve all articles.
- **GET /api/articles/{article_id}**: Retrieve a specific article by ID.
- **GET /api/articles/search**: Search articles by title.
- **POST /api/articles**: Add a new article (Admin or Viewer).
- **PATCH /api/articles/{article_id}**: Update an article.
- **DELETE /api/articles/{article_id}**: Remove an article.

### **Authorization**
- JWT-based authentication ensures secure access to API endpoints.
- Role-based access control (e.g., Admin, Viewer) is supported.

---

## Roles and Permissions

| Role   | Permissions                                        |
|--------|----------------------------------------------------|
| Admin  | Full access to all endpoints.                      |
| Editor | Can view and update articles.                      |
| Viewer | Can view articles and create their own articles.   |

---

## Setup

### **Prerequisites**

- Docker and Docker Compose
- Python 3.9+ (optional for manual setup)
- Poetry (for Python dependency management, optional)
- PostgreSQL database

---

## Installation and Usage

### **1. Clone the Repository**

```bash
git clone <repository_url>
cd <project_directory>
```

### **2. Configure Environment Variables**

Create the `.env` file from the example:

```bash
cp env.example .env
```

Update the `.env` file with your configuration. Example:

```env
DATABASE_URL=postgresql://username:password@host.docker.internal:5432/dbname
SECRET_KEY=my_secret_key
POSTGRES_PASSWORD=my_postgres_password
```

### **3. Build and Start the Application**

Use Docker Compose to build and run the application:

```bash
docker-compose up --build
```

---

## Data Initialization

### **Automatically Generate Sample Data**

Run the following command to create sample data:

```bash
docker-compose exec web poetry run flask create-sample-data
```

### **Manually Create Data via Flask Shell**

1. Access the Flask shell:

   ```bash
   docker-compose exec web poetry run flask shell
   ```

2. Use the following commands to create a new user:

   ```python
   from userarticlesmanager.services.user_service import create_user
   user = create_user("new_user", "1111", "Viewer")
   ```

---

## Testing

Run the test suite with coverage:

```bash
pytest --cov
```

### Test Coverage
The current test coverage is **92%**, ensuring high reliability and robustness of the codebase.

---

## API Endpoints

### **User Management**

- **Authenticate a User**  
  **POST /login**  
  Example Request Body:
  ```json
  {
      "username": "admin",
      "password": "adminpass"
  }
  ```
  Response:
  ```json
  {
      "access_token": "token",
      "message": "Login successful"
  }
  ```

- **List All Users**  
  **GET /api/users**  
  (Admin only)  
  Response:
  ```json
  [
      {
          "id": "1",
          "role": "Admin",
          "username": "admin"
      }
  ]
  ```

- **Search Users by Username**  
  **GET /api/users/search**  
  Query: `?username=<search_term>`  
  (Admin only)

- **Get User by ID**  
  **GET /api/users/{user_id}**  
  (Admin only)

- **Update User**  
  **PATCH /api/users/{user_id}**  
  Request Body:
  ```json
  {
      "username": "new_username",
      "role": "Editor"
  }
  ```

- **Delete User**  
  **DELETE /api/users/{user_id}**  
  (Admin only)

### **Article Management**

- **List All Articles**  
  **GET /api/articles**

- **Search Articles by Title**  
  **GET /api/articles/search**  
  Query: `?title=<search_term>`

- **Get Article by ID**  
  **GET /api/articles/{article_id}**
  Response:
  ```json
  {
      "id": 1,
      "title": "Sample Article",
      "content": "This is the content of the article.",
      "created_at": "2024-12-01T12:00:00Z",
      "user_id": 1
  }
  ```

- **Create an Article**  
  **POST /api/articles**  
  Request Body:
  ```json
  {
      "title": "New Article",
      "content": "This is the content of the article.",
      "user_id": 1
  }
  ```

- **Update Article**  
  **PATCH /api/articles/{article_id}**  
  Request Body:
  ```json
  {
      "title": "Updated Title",
      "content": "Updated Content"
  }
  ```

- **Delete Article**  
  **DELETE /api/articles/{article_id}**

---

## Notes

- Ensure your `.env` file is properly configured before running the application.
- The default admin credentials are included in the sample data setup for initial access.
