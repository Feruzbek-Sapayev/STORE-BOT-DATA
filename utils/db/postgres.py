from typing import Union

import asyncpg
from asyncpg import Connection
from asyncpg.pool import Pool

from data import config


class Database:
    def __init__(self):
        self.pool: Union[Pool, None] = None

    async def create(self):
        self.pool = await asyncpg.create_pool(
            user=config.DB_USER,
            password=config.DB_PASS,
            host=config.DB_HOST,
            database=config.DB_NAME,
        )

    async def execute(
        self,
        command,
        *args,
        fetch: bool = False,
        fetchval: bool = False,
        fetchrow: bool = False,
        execute: bool = False,
    ):
        
        async with self.pool.acquire() as connection:
            connection: Connection
            async with connection.transaction():
                if fetch:
                    result = await connection.fetch(command, *args)
                elif fetchval:
                    result = await connection.fetchval(command, *args)
                elif fetchrow:
                    result = await connection.fetchrow(command, *args)
                elif execute:
                    result = await connection.execute(command, *args)
            return result

    async def create_table_users(self):
        sql = """
        CREATE TABLE IF NOT EXISTS Users (
        id SERIAL PRIMARY KEY,
        full_name VARCHAR(255) NOT NULL,
        username varchar(255) NULL,
        telegram_id BIGINT NOT NULL UNIQUE,
        phone_number VARCHAR NOT NULL
        );
        """
        await self.execute(sql, execute=True)
    async def create_table_cats(self):
        sql = """
        CREATE TABLE IF NOT EXISTS Categories (
        id SERIAL PRIMARY KEY,
        name VARCHAR(255) NOT NULL,
        parent_id INTEGER NULL
        );
        """
        await self.execute(sql, execute=True)

    async def create_table_products(self):
        sql = """
        CREATE TABLE IF NOT EXISTS Products (
        id SERIAL PRIMARY KEY,
        name VARCHAR(255) NOT NULL,
        description TEXT NOT NULL,
        price BIGINT NOT NULL, 
        image VARCHAR(255) NOT NULL,
        category_id INTEGER NOT NULL
        );
        """
        await self.execute(sql, execute=True)
    
    async def create_table_cart(self):
        sql = """
        CREATE TABLE IF NOT EXISTS Cart (
        id SERIAL PRIMARY KEY,
        user_id INT NOT NULL UNIQUE
        );
        """
        await self.execute(sql, execute=True)
    
    async def create_table_cart_items(self):
        sql = """
        CREATE TABLE IF NOT EXISTS CartItem (
        id SERIAL PRIMARY KEY,
        cart_id INT NOT NULL,
        product_id INT NOT NULL,
        quantity INT NOT NULL
        );
        """
        await self.execute(sql, execute=True)
        
    @staticmethod
    def format_args(sql, parameters: dict):
        sql += " AND ".join(
            [f"{item} = ${num}" for num, item in enumerate(parameters.keys(), start=1)]
        )
        return sql, tuple(parameters.values())

    async def add_user(self, full_name, username, telegram_id, phone_number):
        sql = "INSERT INTO users (full_name, username, telegram_id, phone_number) VALUES($1, $2, $3, $4) returning *"
        return await self.execute(sql, full_name, username, telegram_id, phone_number, fetchrow=True)

    async def select_all_users(self):
        sql = "SELECT * FROM Users"
        return await self.execute(sql, fetch=True)

    async def select_user(self, telegram_id):
        sql = "SELECT * FROM Users WHERE telegram_id=$1"
        return await self.execute(sql, telegram_id, fetchrow=True)

    async def count_users(self):
        sql = "SELECT COUNT(*) FROM Users"
        return await self.execute(sql, fetchval=True)

    async def update_user_username(self, username, telegram_id):
        sql = "UPDATE Users SET username=$1 WHERE telegram_id=$2"
        return await self.execute(sql, username, telegram_id, execute=True)

    async def delete_users(self):
        await self.execute("DELETE FROM Users WHERE TRUE", execute=True)
        
    async def delete_products(self):
        await self.execute("DELETE FROM Products WHERE TRUE", execute=True)
        
    async def drop_users(self):
        await self.execute("DROP TABLE Users", execute=True)
        
        # Product 
    async def select_parent_cats(self):
        sql = "SELECT * FROM Categories WHERE parent_id IS NULL"
        return await self.execute(sql, fetch=True)
    
    async def select_cats_from_parent_id(self, id):
        sql = "SELECT * FROM Categories WHERE parent_id = $1"
        return await self.execute(sql, id, fetch=True)

    
    async def add_category(self, name, parent_id):
        sql = "INSERT INTO categories (name, parent_id) VALUES($1, $2) returning *"
        return await self.execute(sql, name, parent_id, fetchrow=True)
    
    async def add_product(self, name, description, price, image, category_id):
        sql = "INSERT INTO products (name, description, price, image, category_id) VALUES($1, $2, $3, $4, $5) returning *"
        return await self.execute(sql, name, description, price, image, category_id, fetchrow=True)
    
    async def get_products(self, category_id):
        sql = "SELECT * FROM Products WHERE category_id = $1"
        return await self.execute(sql, category_id, fetch=True)
    
    async def get_product_by_name(self, product_name):
        sql = "SELECT * FROM Products WHERE name = $1"
        return await self.execute(sql, product_name, fetchrow=True)
    
    async def get_category_by_name(self, name):
        sql = "SELECT * FROM Categories WHERE name = $1"
        return await self.execute(sql, name, fetchrow=True)

