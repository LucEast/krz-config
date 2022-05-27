# Automatic IServ configurator

This code automatically sets the default config and privileges from the  [@krzLemgo](https://github.com/krzLemgo) IServ team.

## Script Setup
- Edit [privileges.csv](./privileges.csv) with your desired privileges
- Install the psycopg2 library 
```
# Install psycopg2 directly
pip3 install psycopg2

# Alternatively, use requirements.txt
pip install -r requirements.txt
```

The script can now simply be called like this:

```
python krzcfg.py
```