# serial2mqtt
serial &lt;-> MQTT bridge

## About

This daemon is inspired in [zigbee2mqtt](https://github.com/Koenkk/zigbee2mqtt) and provides the means to integrate a remote serial port into your Home Assistant setup.

## How to use

### Create a Virtual Environment (recommended) and install the requirements
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Setup systemd
```bash
sudo cp serial2mqtt.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable serial2mqtt.service 
```

### Check everything is OK
```bash
sudo systemctl start serial2mqtt.service 
sudo systemctl status serial2mqtt.service 
```

### Command line arguments and configuration file

When the daemon first runs, it creates a default `config.yaml` file.
You can edit the file to customize your setup.
