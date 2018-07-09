# RailML element splitter

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
