# Project Overview

This repository implements the [https-notif draft](https://datatracker.ietf.org/doc/draft-ietf-netconf-https-notif/) in Python (Flask and Fast API).

## Features

- **Multi-Framework Support**: Implementations in Python (Flask and Fast API).
- **Testing**: Performance tests using `go-wrk`. See [Testing](tests/README.md) for more information

## Getting Started

#### Folder structure: 

```bash
.
├── certs
│   ├── server.crt
│   └── server.key
├── installation.md
├── LICENSE.txt
├── python
│   ├── fast_api_impl
│   │   ├── main.py
│   │   └── README.md
│   ├── flask_impl
│   │   ├── app.py
│   │   ├── docker-compose.yml
│   │   ├── kafka_consumer.py
│   │   ├── read_db.py
│   │   ├── README.md
│   │   ├── requirements.txt
│   └── publisher
│       └── publisher.py
├── README.md
├── tests
│   ├── data
│   │   ├── data.json
│   │   ├── data.xml
│   │   ├── gowrk_script
│   │   ├── plot.py
│   │   ├── script
│   │   └── script2
│   ├── image-1.png
│   ├── image.png
│   ├── lua
│   │   ├── get_seq.lua
│   │   ├── post_json.lua
│   │   ├── post_xml.lua
│   │   ├── rand_seq.lua
│   │   ├── res_track.lua
│   │   └── seq.lua
│   ├── README.md
│   └── setup.png
├── usage.md
└── yang_modules
    ├── ietf-https-notif.yang
    ├── ietf-yang-types.yang
    └── yang-library.json
```

For detailed instructions, see [Installation](installation.md) and [Usage](usage.md).

## Contributing

Pull requests are welcome. For major changes, please open an issue first
to discuss what you would like to change.

Please make sure to update tests as appropriate.


## License

[MIT](https://choosealicense.com/licenses/mit/)

## Contact us 

Bharadwaja Meherrushi Chittapragada (meher.211cs216@nitk.edu.in) <br>
Vartika T Rao (vartikatrao.211it077@nitk.edu.in) <br>
Siddharth Bhat (sidbhat.211ee151@nitk.edu.in) <br>
Hayyan Arshad (hayyanarshad.211cs222@nitk.edu.in) <br>


