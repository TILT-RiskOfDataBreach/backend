FROM mongo:6.0

COPY users.json /users.json
COPY tilts.json /tilts.json
COPY risks.json /risks.json

CMD mongoimport --host mongo --db data -u root -p SuperSecret --collection users --type json --file /users.json --jsonArray && \
    mongoimport --host mongo --db data -u root -p SuperSecret --collection tilts --type json --file /tilts.json --jsonArray && \
    mongoimport --host mongo --db data -u root -p SuperSecret --collection risks --type json --file /risks.json --jsonArray
