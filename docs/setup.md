# Setup

## Prerequisites

Make sure these are installed:

- [Docker](https://www.docker.com/)
- [uv](https://github.com/astral-sh/uv)

## Optional Kaggle authentication

This project uses a public Kaggle dataset. In some environments, the dataset download may work without explicit authentication.

If Kaggle requires authentication, provide your token locally before starting the project.

### Option 1: export the token in your shell

```bash
export KAGGLE_API_TOKEN='your_real_token_here'
````

### Option 2: create a local `.env` file

```env
KAGGLE_API_TOKEN=your_real_token_here
```

Do not commit this file.

## Project setup

Start the project with Docker:

```bash
docker compose up --build
```
