import asyncio
import os

from dotenv import load_dotenv

import db

load_dotenv()



async def main():
    host = os.getenv("DB_HOST", "127.0.0.1")
    port = int(os.getenv("DB_PORT", "3306"))
    user = os.getenv("DB_USER")
    passwd = os.getenv("DB_PASS")
    table = os.getenv("DB_NAME")
    await db.init_pool(host, port, user, passwd, table)
    time = await db.fetchone("SELECT NOW()")
    print(str(time['NOW()']).split(" "))
    
if __name__ == "__main__":
    asyncio.run(main())