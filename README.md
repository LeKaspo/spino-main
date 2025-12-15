# Spino

This is a Spionaustier repo

![Picture of Roboter](https://cdn11.bigcommerce.com/s-yo2n39m6g3/images/stencil/1280x1280/products/2785/11421/71Xrm2EZF7L__50140.1723978723.jpg?c=2?imbypass=on)

## Ausführung:

```bash
# Auf dem Server
# Python3.11 installieren
cd spino-main
python -m venv spino_venv

# Wenn der Server Linux verwendet:
source .\spino_venv\bin\activate
# Wenn der Server Windows verwendet:
spino_venv\Scripts\activate

pip install -r requirements_server.txt
python .\src\server\app\main.py

# Auf dem Roboter, nachdem die IP des Laptops in .\src\server\config\config.py eingestellt wurde:
# Python3.12 installieren
cd spino-main
python -m venv spino_venv
source .\spino_venv\bin\activate
pip install -r requirements_robo.txt
python3 .\src\robo\main\main.py
```
Dann im Browser öffnen (http://localhost:50004/)