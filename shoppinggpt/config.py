"""Centralized, portable configuration for the ShoppingGPT legacy application."""
import os
from pathlib import Path
from dotenv import load_dotenv
from langchain_google_genai import GoogleGenerativeAIEmbeddings

ROOT = Path(__file__).resolve().parents[1]
load_dotenv(ROOT / ".env")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
DATA_PRODUCT_PATH = str(ROOT / "data" / "products.db")
DATA_TEXT_PATH = str(ROOT / "data" / "policy.txt")
STORE_DIRECTORY = str(ROOT / "data" / "datastore")
EMBEDDINGS = GoogleGenerativeAIEmbeddings(model=os.getenv("EMBEDDING_MODEL", "models/embedding-001"))
