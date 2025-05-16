# Project Overview

This repository implements the [IETF HTTPS Notification draft](https://datatracker.ietf.org/doc/draft-ietf-netconf-https-notif/) using **Python**, with both **Flask** and **FastAPI** frameworks.

## Draft Overview

The HTTPS Notification draft defines a protocol for sending **asynchronous event notifications over HTTPS**, similar to those in [RFC 5277](https://datatracker.ietf.org/doc/rfc5277/), over HTTPS. 

This enables a secure and flexible mechanism for delivering event notifications over standard web infrastructure.

## CBOR Encoding Support
  Added support for **CBOR (Concise Binary Object Representation)** encoding, in addition to the JSON and XML formats already described in the draft. This enhances performance in bandwidth-constrained environments.

-  **Internet-Draft for CBOR Extension**  
  Our CBOR encoding extension is documented in a separate Internet-Draft:  
   [draft-chittapragada-netconf-https-notif-cbor](https://datatracker.ietf.org/doc/draft-chittapragada-netconf-https-notif-cbor/)

-  **Presentation at IETF**  
  We presented our CBOR extension and implementation at an IETF meeting:  
  [Watch the presentation](https://youtu.be/VVUIz-OsGbo?t=6371)

##  Goal

This project serves as a reference implementation and experimentation ground for the HTTPS-notif protocol and its extensions. It’s designed for researchers, implementers, and contributors in the IETF NETCONF working group and broader network automation community.



Feel free to open issues or contribute if you'd like to extend or integrate this work!


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
│   │   ├── prometheus.yml
│   │   ├── __pycache__
│   │   │   ├── app.cpython-312.pyc
│   │   │   └── app.cpython-38.pyc
│   │   ├── read_db.py
│   │   ├── README.md
│   │   └── requirements.txt
│   ├── publisher
│   │   ├── data.xml
│   │   ├── publisher.py
│   │   └── requirements.txt
├── README.md
├── tests
│   ├── data
│   │   ├── data.cbor
│   │   ├── data.json
│   │   ├── data.xml
│   │   ├── gowrk_script
│   │   ├── plot.py
│   │   ├── script
│   │   ├── script2
│   │   └── test1
│   │       ├── results_cbor_100mbit.txt
│   │       ├── results_cbor_10mbit.txt
│   │       ├── results_cbor_1gbit.txt
│   │       ├── results_cbor_1mbit.txt
│   │       ├── results_cbor_500mbit.txt
│   │       ├── results_cbor_50mbit.txt
│   │       ├── results_cbor_5mbit.txt
│   │       ├── results_json_100mbit.txt
│   │       ├── results_json_10mbit.txt
│   │       ├── results_json_1gbit.txt
│   │       ├── results_json_1mbit.txt
│   │       ├── results_json_500mbit.txt
│   │       ├── results_json_50mbit.txt
│   │       ├── results_json_5mbit.txt
│   │       ├── results_xml_100mbit.txt
│   │       ├── results_xml_10mbit.txt
│   │       ├── results_xml_1gbit.txt
│   │       ├── results_xml_1mbit.txt
│   │       ├── results_xml_500mbit.txt
│   │       ├── results_xml_50mbit.txt
│   │       └── results_xml_5mbit.txt
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


