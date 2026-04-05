from config import PG_CONN_STR, DOC_NAME
from db import count_chunks

if __name__ == "__main__":
    count = count_chunks(PG_CONN_STR, DOC_NAME)
    print(f"Current count for '{DOC_NAME}': {count}")
