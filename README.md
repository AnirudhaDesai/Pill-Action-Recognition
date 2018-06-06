# Pill-Action-Recognition
ML based Pill Action Recognition  

## Server Setup
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

## Models

There are 3 models that are available to use (others can be added easily, more on that later), I also mention how to set a few of the hyperparameters of the model by modifying `config.json` -    
  * **Touch** Uses touch duration to predict an intake. To use this model set `config.model.type = "Touch"`. Touch duration is set by `config.model.touch_threshold`. Main code file is `Code/server/touch_predictor.py`.
  * **Ensemble** Uses 4 different models to predict each action involved in pill ingestion. To use this set `config.model.type = "Ensemble"`. To decide which features to use we use `config.model.features`. `config.model.path` should specify the directory in which all 4 models are located (in .pkl format). Main code file is `Code/server/ensemble_predictor.py`
  * **Binary** Uses a single binary classifier. To use this set `config.model.type = "Binary"`. To decide which features to use we use `config.model.features`. `config.model.path` should specify the directory in which the trained model is located (in .pkl format). Main code file is `Code/server/binary_predictor.py`.

Note that even though the **Ensemble** and **Binary** models might appear very similar, they differ in one key aspect, the ground truth *labels* needed to train them. The **Ensemble** model requires ground truth to possess labels to indicate each distinct action for any sequence of sensor data, while the **Binary** model only requires a label to indicate that medication intake occured (or not) in any sequence of sensor data. This makes training them quite different even though the data they use is the same.

**FUN FACT -** Since there is no way to collect ground data for the **Ensemble** model (right now), we can't use it for the pilot! We have to use the **Binary** clf. Also since we don't have a trained **Binary** clf available right from the start, we require a model roll-out plan to train this model first. I describe it below.

### Model Roll-Out Plan
A simple way we could do this is by first using the **Touch** predictor for the beginning of the pilot with a low enough touch duration value so that most touches trigger a *true* prediction from the system. This will in turn initiate a push-notification to the phone-app, which shows up in the form of a question to the user - *Did you just take xyz med?*. Whatever may be the answer to this question, we use it as ground truth. We have to use this way to ensure we are able to collect as much ground truth data as possible, thus we keep the touch duration low so that we trigger these chain of events quite frequently.  

When we believe a considerable amount of data has been collected we  do the following -  
  * We hit the training data extraction endpoint, when setup locally it resolves to the path `localhost:5000/extract_training_data`. This endpoint compiles and stores all the training data that we'll need in a *.npz* file in the directory given by `config.model.path_to_data`. 
  * You now need to use the file `Code/FeatureExtraction.py` to generate a set of *.npy* files which contain the features we need, you might need to modify the variable `path` and `datafile` to be able to use the *.npz* file we created in the previous step. I'd recommend changing the code so as to be able to accept the path as a command line argument as this would make it possible for you to run it remotely on the server machine so that the new files created/used are already available on that (physical) machine.
  * Finally, we use the file `Code/model.py` to train the model. There are a couple of hyper-parameters (stored as global variables) for this file too. Again, I would advise adding code to be able to set these params from the command line. This file will perform cross-validation by using a hold-out set, it will repeat the cross validation with randomized hold-out sets 500 times, if it's taking too long (which I believe it will when we have some non-trivial amount of data) you can reduce it, I'd still keep it around 50 if feasible.
    * `DIRECTORY` would be the directory of where the *.npz* file was kept. 
    * `TEST_SAMPLES` would be the number of samples to use for the validation set during cross validation.
    * `TRAINING_MODEL` "Binary" or "Ensemble".
    * `CLASS_TO_BE_TESTED` keep 1 for "Binary"

After the last step, the model(s) will be stored in path `model/` as *.pkl* files. The server will pickup these models after you change the config file and reset the config. Rejoice! You're done!
