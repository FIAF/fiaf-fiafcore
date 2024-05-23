# FIAF → FIAFcore
FIAF data conformed to FIAFcore.

**Datasets**

[FIAF](https://www.fiafnet.org/)     
[FIAF Members](https://www.fiafnet.org/pages/Community/Members.html)      
[FIAF Associates](https://www.fiafnet.org/pages/Community/Associates.html)  
[FIAF Congresses](https://www.fiafnet.org/pages/History/Archival-Documents-about-FIAF-Congresses.html)

**Process**

The etl process expects an `.env` file

```sh
graph_username= # GraphDB username
graph_password= # GraphDB password
```

The etl script should be run from a virtualenv

```sh
virtualenv venv -p 3.10
source venv/bin/activate
pip install -r requirements.txt
python etl.py
```

**License**

Data is licensed as [CC-BY-4.0](https://creativecommons.org/licenses/by/4.0/). Code is MIT.
