# Pill-Action-Recognition
ML based Pill Action Recognition
### Server Setup
Before you can run the server you need the following libraries. Note that we use **python 3**.  
  1. flask 0.12.2 -> `pip install flask`
  2. google-auth 1.4.1 -> `pip install google-auth`
  3. numpy 1.13.1 -> `pip install numpy`
  4. sqlalchemy 1.2.6 -> `pip install sqlalchemy`
  5. pyfcm 1.4.5 -> `pip instal pyfcm`
  6. Flask-DebugToolbar 0.10.1 -> `pip install Flask-DebugToolbar`
  7. pymysql - 0.8.0 -> `pip install pymysql`

I recommend using `pip` instead of `conda` or other package managers as I remember at least one of the above was only available through pip. 

Next, you need a **mysql** server running. You can get **mysql** [here](https://dev.mysql.com/downloads/mysql/) you might want to install the **mysql** workbench as well, it makes life much more easier. During installation you should be asked to create an instance and a root password, remember both the user-name and root password that you set here. Also, create a DB instance, again remember its name. Now, go to the file `\Code\config.json` and update the file with the user-name, pass and DB name that you set, you can find these entries under the 'db' object name in the json file. The entry should look like this -  
```
"db": {
  "name": "name_of_db_you_created",
  "user": "user_name_for_db",
  "pass": "root_password_for_db",
  "port": "port_number"
}
```

You probably won't need to change the port number.

After the requirements are met, you are ready to start the server.  

First, start your instance of **mysql**. Now start the python server with the following commands, make sure to `cd` into the server directory first!
  * **Windows CMD**
    ```
    SET FLASK_APP=server.py
    python -m flask run
    ```
  * **Bash**
    ```
    $ export FLASK_APP=server.py
    $ python -m flask run
    ```

It should take a few seconds on the first try as it will create all the tables in your DB. If you installed the **mysql** workbench you should be able to see all the changes to the DB on it. If everything goes fine, try and hit `localhost:5000/` from your browser you should see the flask debug toolbar stuff come up. And that's all folks!
