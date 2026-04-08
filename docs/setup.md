# Setup

## Prerequisites

Make sure these are installed:

- [Docker](https://www.docker.com/)
- [uv](https://github.com/astral-sh/uv)

## Optional Kaggle authentication

This project uses a public Kaggle dataset. In some environments, the dataset download may work without explicit authentication.

## Kaggle API Token

This project downloads a dataset from Kaggle.  
To access the dataset, you need a personal Kaggle API token.

### Step 1 – Create a Kaggle account

1. Go to https://www.kaggle.com
2. Create an account or log in

### Step 2 – Open the account settings

1. Open https://www.kaggle.com/settings
2. Scroll to the **API** section

### Step 3 – Create a new token

1. Click **Create New Token**

### Step 4 – Define a name for the token

1. Enter a name for your token
2. Confirm the creation

### Step 5 – Copy the token

After creating the token, Kaggle will show it once in a popup.  
Copy the token directly from there.

---

### Step 6 – Create a `.env` file

1. Copy the file `.env.example` in the project
2. Rename the copy to:

```
.env
```

3. Open `.env`
4. Paste your token:

```env
KAGGLE_API_TOKEN=your_token_here
```

---

**Important:**  
The token is only shown once. If you do not copy it, you will need to create a new one.

The `.env` file contains sensitive credentials and must **not be committed** to GitHub.


## Project setup

Start the project with Docker:

```bash
docker compose up --build
```
