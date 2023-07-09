# TILT-RiskOfDataBreach Backend

This system represents a PoC for the assessment of a risk of a data breach, based on data sharing networks that are enriched with data about historic data breaches. The implementation is guided by the [transparency information language and toolkit](https://github.com/Transparency-Information-Language/meta).

## Startup

 `docker-compose up`


## Database Setup

The Docker Compose setup will automatically create a `data` database with `tilts`, `risks`, and `users` collections in it.

These collections will be filled with dummy-data by the `dbseed` service. You now can interact with our API on the admin level through the user `(username: admin, password: SuperSecret)`.

*Note:* To reset the database (**this will delete all data**), remove the Docker volume `backend_mongodata`. As long as this volume is present, initialization scripts will have no impact.

To force an image rebuild on docker compose, run:

`docker compose up --build`

## Services

Our backend consists of three services: `analysis-engine`, `risk-engine`, and `tilt-engine`.

## Analysis-Engine

The `Analysis-Engine` is used to estimate the risk posed by a data controller based on information extracted from associated `TILTs`. The service extracts a data sharing network and additional meta data from all available `TILTs` and uses structural information from the network and the additional meta data for the risk estimate.

### API

#### Definition - access_lvl
- 0: Default, can update data sharing network and risk estimates
- 1: Admin, has admin access


#### Documentation

##### `/docs`

- GETs interactive documentation web page


#### Analysis

##### `/update`

- is run on startup and once a day
- runs risk analysis algorithm outside of the aforementioned events
- access_lvl: 0 & 1

Header:
```json
{
 "access_token": "str"
}
```

GET:
```json
{ }
```

Response:
```json
{
 "acknowledged": "bool"
}
```


#### Authentication

##### `/token`

- generates session and refresh token

POST (x-www-form-urlencoded): 
```
{
 username: str
 password: str
}
```

Response: 
```json
{  
 "access_token": "str",
 "refresh_token": "str",
 "token_type": "str",
 "access_lvl": "int"
}
```

##### `/refresh`

- generates new session token

Header:
```json
{
 "refresh_token": "str"  
}
```

GET: 
```
{ }
```

Response: 
```json
{  
 "access_token": "str",
 "token_type": "str",
 "access_lvl": "int"
}
```


#### Login

##### `/is_username/{username}`

- checks if username exists
- access_lvl: 0 & 1

Header:
```json
{
 "access_token": "str"
}
```

GET:
```json
{
 "username": "str"
}
```

Response:
```json
{
 "is_username": "bool"
}
```


##### `/signup`

- signups new user
- access_lvl: 0 & 1

Header:
```json
{
 "access_token": "str"  
}
```

POST:
```json
{
 "username": "str",
 "password": "str",
 "company": "str",
 "country": "str",
 "address": "str",
 "access_lvl": "int"
}
```

Response:
```json
{
 "acknowledged": "bool"
}
```

## Risk-Engine

The `Risk-Engine` returns the estimated risks with the for the risk estimation extracted data.

### API

#### Definition - access_lvl
- Public!


#### Documentation

##### `/docs`

- GETs interactive documentation web page


#### Risks

##### `/{domain}`

- returns risk estimate with additional meta data used in the calculation
- access_lvl: Public!

GET:
```json
{
 "domain": "str"
}
```

Response:
```json
{
        "domain": "str",
        "riskScore": "float",
        "avgSeverityOfBreaches": "int",
        "similarBreachedDomains": [
            {
                "domain": "str",
                "breaches": "int",
                "cluster": "int",
                "severity": "int",
                "articleRank": "float",
                "betweenness": "float",
                "degree": "float",
                "harmonicCloseness": "float"
            }
        ],
        "similarNodes": [
            {
                "domain": "str",
                "breaches": "int",
                "cluster": "int",
                "severity": "int",
                "articleRank": "float",
                "betweenness": "float",
                "degree": "float",
                "harmonicCloseness": "float"
            }
        ],
        "validMeasuresInCluster": [
            {
                "cluster": "int",
                "articleRank": "bool",
                "betweenness": "bool",
                "degree": "bool",
                "harmonicCloseness": "bool"
            }
        ]
    }
```

## TILT-Engine

The `TILT-Engine` inserts, updates, or deletes `TILTs` upon request from certified sources.

### API

#### Definition - access_lvl
- 0: Default, can update data sharing network and risk estimates
- 1: Admin, has admin access


#### Documentation

##### `/docs`

- GETs interactive documentation web page


#### TILTs

##### `/tilt/insert`

- inserts or updates one `TILT` document
- access_lvl: 0 & 1

Header:
```json
{
 "access_token": "str"
}
```

POST:
`[TILT](https://github.com/Transparency-Information-Language/schema)`

Response:
```json
{
 "acknowledged": "bool"
}
```

##### `/tilts/insert`

- inserts or updates many `TILT` documents
- access_lvl: 0 & 1

Header:
```json
{
 "access_token": "str"
}
```

POST:
`[[TILT](https://github.com/Transparency-Information-Language/schema)]`

Response:
```json
{
 "acknowledged": "bool"
}
```

##### `/{domain}/delete`

- deletes one `TILT` document
- access_lvl: 0 & 1

Header:
```json
{
 "access_token": "str"
}
```

DELETE:
```json
{
 "domain": "str"
}
```

Response:
```json
{
 "acknowledged": "bool"
}
```


#### Authentication

##### `/token`

- generates session and refresh token

POST (x-www-form-urlencoded): 
```
{
 username: str
 password: str
}
```

Response: 
```json
{  
 "access_token": "str",
 "refresh_token": "str",
 "token_type": "str",
 "access_lvl": "int"
}
```

##### `/refresh`

- generates new session token

Header:
```json
{
 "refresh_token": "str"  
}
```

GET: 
```
{ }
```

Response: 
```json
{  
 "access_token": "str",
 "token_type": "str",
 "access_lvl": "int"
}
```


#### Login

##### `/is_username/{username}`

- checks if username exists
- access_lvl: 0 & 1

Header:
```json
{
 "access_token": "str"
}
```

GET:
```json
{
 "username": "str"
}
```

Response:
```json
{
 "is_username": "bool"
}
```


##### `/signup`

- signups new user
- access_lvl: 0 & 1

Header:
```json
{
 "access_token": "str"  
}
```

POST:
```json
{
 "username": "str",
 "password": "str",
 "company": "str",
 "country": "str",
 "address": "str",
 "access_lvl": "int"
}
```

Response:
```json
{
 "acknowledged": "bool"
}
```


## Security

Replace the `SECRET_KEY` in `src/constants.py` with your own, using the following command:

`openssl rand -hex 32`

Change the `password` property (and other properties if you want to) in `dbseed/init-admin.json`, by aquiring a new password using the following command:

`from passlib.context import CryptContext`

`CryptContext(schemes=["bcrypt"], deprecated="auto").hash("respective_password")`