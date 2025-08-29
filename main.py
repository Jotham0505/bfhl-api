# main.py
import os
import re
from typing import List, Any
from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel
from fastapi.responses import JSONResponse
from dotenv import load_dotenv

# load .env if present
load_dotenv()

app = FastAPI(title="BFHL API - /bfhl")

FULL_NAME = os.getenv("BFHL_FULL_NAME", "john_doe").strip().lower().replace(" ", "_")
DOB_DDMMYYYY = os.getenv("BFHL_DOB", "17091999").strip() 
EMAIL = os.getenv("BFHL_EMAIL", "john@xyz.com").strip()
ROLL_NUMBER = os.getenv("BFHL_ROLL", "ABCD123").strip()

USER_ID = f"{FULL_NAME}_{DOB_DDMMYYYY}"

class DataIn(BaseModel):
    data: List[Any]

_digits_re = re.compile(r'^\d+$')
_alpha_re  = re.compile(r'^[A-Za-z]+$')

def process_items(items: List[Any]):
    even_numbers: List[str] = []
    odd_numbers: List[str] = []
    alphabets: List[str] = []
    special_characters: List[str] = []
    total_sum = 0

    alpha_chars: List[str] = []

    for v in items:
        s = str(v)
        s_stripped = s.strip()

        
        for ch in s_stripped:
            if ch.isalpha():
                alpha_chars.append(ch)

        
        if _digits_re.fullmatch(s_stripped):
            num = int(s_stripped)
            total_sum += num
            if num % 2 == 0:
                even_numbers.append(str(num))
            else:
                odd_numbers.append(str(num))
            continue

        
        if _alpha_re.fullmatch(s_stripped):
            alphabets.append(s_stripped.upper())
            continue

        
        special_characters.append(s)

    concat_chars = []
    for idx, ch in enumerate(reversed(alpha_chars)):
        concat_chars.append(ch.upper() if idx % 2 == 0 else ch.lower())
    concat_string = "".join(concat_chars)

    response = {
        "is_success": True,
        "user_id": USER_ID,
        "email": EMAIL,
        "roll_number": ROLL_NUMBER,
        "odd_numbers": odd_numbers,
        "even_numbers": even_numbers,
        "alphabets": alphabets,
        "special_characters": special_characters,
        "sum": str(total_sum),
        "concat_string": concat_string
    }

    return response

@app.post("/bfhl")
async def bfhl_endpoint(payload: DataIn, request: Request):
    try:
        data_list = payload.data
        if not isinstance(data_list, list):
            raise HTTPException(status_code=400, detail="`data` must be a list.")
        resp = process_items(data_list)
        return JSONResponse(status_code=200, content=resp)
    except HTTPException:
        raise
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={
                "is_success": False,
                "error": "Internal server error",
                "details": str(e),
                "user_id": USER_ID,
                "email": EMAIL,
                "roll_number": ROLL_NUMBER
            }
        )
