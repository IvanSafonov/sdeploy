# sdeploy
Simple remote deployment tool for linux. It's used for uploading any files to the remote linux system during development. This script archives changed files (optional all) then sends archive to the remote host over SSH and unpacks it's there. Also it can run commands before or after uploading. Depends on **paramiko**.

# How to use
In the root of project (optional wherever you like) you need to create config file in JSON format (see below) and run main script.
```
sdeploy -a 192.168.0.1 -p 2222 -u root -p 111 -b build -k mainapp
```

```
All available options:
  -h, --help            show this help message and exit
  -a HOST, --host=HOST  remote linux machine host
  -p PORT, --port=PORT  ssh port, 22 by default
  -u USER, --user=USER  ssh user name
  -s PASSWORD, --password=PASSWORD
                        ssh password
  -k KIT, --kit=KIT     comma separated list of kits, all kits in config if
                        not set
  -c CONFIG, --config=CONFIG
                        .json config file, deployment.json by default
  -b BUILDDIR, --buildDir=BUILDDIR
                        build directory
  -f, --fullUpdate      send all files
  -t, --strip           strip binary files
  -z, --zip             using zip compression
```

# Config file example
```json
{
    "corelib" : {
        "files": [
            {
                "src": "%{buildDir}/core/libFooBar.so",
                "dest": "/opt/foobar/lib/"
            },
            {
                "src": "config/main.ini",
                "dest": "/opt/foobar/conf/"
            },
            {
                "src": "%{buildDir}/plugins",
                "dest": "/opt/foobar/plugins",
                "mask": "lib.*\\.so",
                "exclude": "libSomeFile.so"
            }
        ]
    },
    "mainapp" : {
        "preInstall": [
            "stop myservice"
        ],
        "files": [
            {
                "src": "%{buildDir}/bin/mainapp",
                "dest": "/opt/foobar/bin/"
            }
        ],
        "postInstall": [
            "start myservice"
        ],
        "kits": ["corelib"]
    }
}
```
```corelib``` and ```mainapp``` is the kits.
Kit options:
* ```files``` - list of files that sent to the remote host
  * ```src``` - source file or directory path. Directories are copied recursively. Template ```%{buildDir}``` is replaced with current build directory.
  * ```dest``` - target path on the remote host
  * ```mask``` - pattern to selectively copying files
  * ```exclude``` - pattern to selectively exclude certain files
* ```preInstall``` - list of commands that will be executed before copying files
* ```postInstall``` - list of commands that will be executed after copying files
* ```kits``` - other included kits



