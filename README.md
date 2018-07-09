# RailML element splitter

To start the microservice:
docker run -d --name railml-microservice -p 9290:5000 sesam/railml-microservice:latest

## How to configure

```json
{
  "_id": "railml",
  "type": "system:microservice",
  "docker": {
    "image": "[..]",
    "port": 5000,
    "environment": {
      "GIT_URL": "git@github.com:datanav/railml-microservice.git",
      "FILE_PATTERN": "testfiles/*",
      "SSH_PRIVATE_KEY": "-----BEGIN RSA PRIVATE [..]"  
    }
  }
}
```

## How to use

Pull down the different elements by requesting the following patterns '/track', '/signal', etc.