# SOUP AI-Powered Core

## Overview

This repository contains the ai core for the SOUP AI-powered learning platform. It provides services for generating and evaluating student level tests, as well as creating personalized study planners. The application is built with FastAPI and leverages graph-based workflows for complex logic.

## Features

- **Level Test Generation**: Dynamically creates level-appropriate tests for students based on specified workbooks and units.
- **Level Test Evaluation**: Evaluates student answers for both multiple-choice and descriptive questions. It includes OCR capabilities to process image-based answers.
- **Personalized Study Planner**: Generates a customized study plan for a student based on their recent performance and learning history.

## API Endpoints

The API is versioned and all endpoints are available under the `/v1` prefix.

### Level Test

- **POST** `/v1/level-test/generate`
  - **Description**: Generates a new level test for a student.
  - **Request Body**:
    ```json
    {
      "soup_level": "level of study planner soup",
      "workbooks": ["student workbook"],
      "unit_list": ["unit_1", "unit_2"]
    }
    ```
  - **Response**:
    ```json
    {
      "level_test": { ... }
    }
    ```

- **POST** `/v1/level-test/evaluate`
  - **Description**: Evaluates a submitted level test. It can handle both text-based and image-based answers.
  - **Request Body**:
    ```json
    {
      "level_test_result": [
        {
          "text": "Question text...",
          "answer": "Correct answer...",
          "user_answer_text": "Student's text answer...",
          "user_answer_image": "path/to/image.png"
        }
      ]
    }
    ```
  - **Response**:
    ```json
    {
      "evaluate_result": [ ... ]
    }
    ```

### Planner

- **POST** `/v1/planner/generate`
  - **Description**: Generates a new personalized study planner for a student.
  - **Request Body**:
    ```json
    {
      "student_id": "student123",
      "date": "2025-11-11"
    }
    ```
  - **Response**:
    ```json
    {
      "planner": { ... }
    }
    ```

## How to Run with Docker

### Prerequisites

- Docker must be installed and running on your system.

### 1. Build the Docker Image

Build the image from the project root directory:

```sh
docker build -t <IMAGE_NAME>:<TAG> .
```

**Example**:
```sh
docker build -t soup-ai-core:latest .
```

### 2. Run the Docker Container

Run the container, mapping port 8000 on the host to port 8000 in the container:

```sh
docker run -d -p 8000:8000 <IMAGE_NAME>:<TAG>
```

**Example**:
```sh
docker run -d -p 8000:8000 soup-ai-core:latest
```

The application will be accessible at `http://localhost:8000`.
