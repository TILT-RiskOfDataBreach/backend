
# MongoDB datasource constants
MONGO = {
    'DATABASE': 'data',
    'HOST': 'localhost',
    'DOCKER': 'mongo',
    'PORT': 27017,
    'USERNAME': 'root',
    'PASSWORD': 'SuperSecret',
    'AUTHENTICATION_SOURCE': 'admin'
}

# Neo4j datasource constants
NEO4J = {
    'DOCKER_URI': 'neo4j://neo4j:7687',
    'URI': 'neo4j://localhost:7687',
    'Username': 'neo4j',
    'Password': 'SuperSecret'
}

JWT = {
    'SECRET_KEY': "610c6f6b5bfb43dc8f62aa9599062be51df1c1632550288b3d4472b95c399564",
    'SECRET_REFRESH_KEY': "f435e2e43fdfc4672da6e4f59568319ac45487832646e720d958367a96881750",
    'ALGORITHM': "HS256",
    'ACCESS_TOKEN_EXPIRE_MINUTES': 30,
    'REFRESH_TOKEN_EXPIRE_MINUTES': 60 * 24 * 7,
    'ACCESS_TOKEN_EXPIRE_SECONDS': 1
}
