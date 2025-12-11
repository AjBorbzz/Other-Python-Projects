from typing import Any, Dict, List, Optional, Tuple 
import re
from fastapi import FastAPI
from pydantic import BaseModel, Field

app = FastAPI(title= "SIEM Log Normalizer and Data Masker")