// MongoDB initialization for mood_tracker
db = db.getSiblingDB('mood_tracker');

// Users collection
db.createCollection('users');
db.users.createIndex({ "email": 1 }, { unique: true });

// Moods collection
db.createCollection('moods');
db.moods.createIndex({ "user_id": 1, "logged_date": 1 }, { unique: true });
db.moods.createIndex({ "user_id": 1 });
db.moods.createIndex({ "logged_date": 1 });

print("mood_tracker database initialized with indexes");

// Also initialize dev database
db = db.getSiblingDB('mood_tracker_dev');

db.createCollection('users');
db.users.createIndex({ "email": 1 }, { unique: true });

db.createCollection('moods');
db.moods.createIndex({ "user_id": 1, "logged_date": 1 }, { unique: true });
db.moods.createIndex({ "user_id": 1 });
db.moods.createIndex({ "logged_date": 1 });

print("mood_tracker_dev database initialized with indexes");
