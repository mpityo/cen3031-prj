from pymongo import MongoClient
from pymongo.server_api import ServerApi
import bcrypt
from .config import Config


class Database:
    def __init__(self):
        self.user_database = self.get_database()
        self.user_list = self.user_database.test_collection

    @staticmethod
    def get_database():
        # Create a connection using MongoClient. You can import MongoClient or use pymongo.MongoClient
        client = MongoClient(Config.DB_CONNECTION)

        # Create the database for our example (we will use the same database throughout the tutorial

        return client.test_database

    @staticmethod
    def test():
        uri = Config.DB_CONNECTION
        # Create a new client and connect to the server
        client = MongoClient(uri, server_api=ServerApi('1'))
        # Send a ping to confirm a successful connection
        try:
            client.admin.command('ping')
            print("Pinged your deployment. You successfully connected to MongoDB!")
        except Exception as e:
            print(e)

    @staticmethod
    def hash_and_salt_password(password):
        salt = bcrypt.gensalt()
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt)

        return  hashed_password, salt

    # temp check for hash
    @staticmethod
    def verify_password(password, stored_salt, stored_hash):
        combined_password = password.encode('utf-8')
        combined_hash = bcrypt.hashpw(combined_password, stored_salt)
        return combined_hash == stored_hash

    def check_username(self, username):
        if self.user_list.find_one({"username": username}):
            return False
        return True

    def register_user(self, username, password):
        # Check if the username already exists
        if self.user_list.find_one({"username": username}):
            return "Username already exists. Please choose another."

        # Hash and salt the password (you'll need a hashing library)
        # Then, store the hashed password in the database
        hashed_password, salt = self.hash_and_salt_password(password)

        # Insert the user document into the collection
        user = {
            "username": username,
            "password": hashed_password,
            "salt" : salt
        }
        self.user_list.insert_one(user)
        self.create_user_collection(username)

        return "Registration successful."


    def login_user(self, username, password):
        user = self.user_list.find_one({"username": username})

        if user:
            stored_hashed_password = user.get("password")
            stored_salt = user.get("salt")
            # Verify the password (implement password verification)
            if self.verify_password(password, stored_salt, stored_hashed_password):
                return "Login successful."
            else:
                return "Invalid password. Please try again."
        else:
            return "Username not found. Please register an account."

    def create_user_collection(self, username):
        # Create a new collection based on the username
        new_collection = self.user_database[username]

        # Must insert data for collection to get created
        new_collection.insert_one({"example_key": "example_value"})
        return new_collection


    def get_user_collection(self, username):
        return self.user_database[username]

    def delete_account(self, username):

        if self.delete_user_collection(username):
            user = self.user_list.delete_one({"username": username})

        return "Account successfully deleted"

    #use as part of deleting a user's account
    def delete_user_collection(self, username):
        if username in self.user_database.list_collection_names():
            self.user_database[username].drop()
            return True
        else:
            return False

    #use to delete chat history
    def delete_data_in_user_collection(self, username):
        # Check if the collection exists before attempting to delete data
        if username in self.user_database.list_collection_names():
            filter_query = {}  # An empty filter will match all documents in the collection
            result = self.user_database[username].delete_many(filter_query)
            return f"{result.deleted_count} document(s) deleted from '{username}' collection."
        else:
            return f"Collection for '{username}' not found."

 #update log to server after exiting program
    def add_chat_log_to_user_collection(self, username, log):
        user_collection = self.get_user_collection(username)
        user_collection.insert_one(log)

        return f"Chat successfully updated to server"

    #retrieve data from server
    def get_all_data_from_collection(self, username):
        user_collection = self.get_user_collection(username)
        projection = {"_id": 0}
        all_data_cursor = user_collection.find({}, projection)
        all_data = list(all_data_cursor)

        return all_data
