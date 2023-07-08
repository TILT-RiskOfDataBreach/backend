db = new Mongo().getDB("data");

db.createCollection("users");
db.createCollection("risks");

db.createUser({
    user: 'root',
    pwd: 'SuperSecret',
    roles: [
        {
            role: 'readWrite',
            db: 'data',
        },
    ],
});
