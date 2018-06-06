# Pill-Action-Recognition
ML based Pill Action Recognition <- (we've come a long way from this)

## Index
This was getting long, so here's some help -

  * [Server Setup](#server-setup)
  * [Config System](#config-system)
    * [Adding a Config Element](#adding-a-config-element)
    * [Updating a Config Element](#updating-a-config-element)
  * [Models](#models)
    * [Model RollOut Plan (UNTESTED)](#model-rollout-plan)
  * [Queueing Service](#queueing-service)
    * [Enqueue](#enqueue)
    * [Dispatch](#dispatch)
  * [Prediction Service](#prediction-service)
    * [Predict](#predict)
    * [Confirm Prediction (UNTESTED)](#confirm-prediction)
    * [Adding a New Predictor](#adding-a-new-predictor)

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

## Config System
We have a fairly easy to use config system in place which allows for dynamic editing of various parameters relating to the server. This system works by pulling out the values of various named and heirarchied elements from the file `Code/config.json`. To use this system in your code, you can simply use an object of class `Helpers` from `Code/server/helpers.py`. Note that this class is [Singleton](https://en.wikipedia.org/wiki/Singleton_pattern), personally, I wouldv'e kept this as a static class ([the pythonic way](https://stackoverflow.com/questions/30556857/creating-a-static-class-with-no-instances)) instead as it's essentially a utils class but I guess this is what we started with and I never got to changing it. You can get the value of any config element in the config file you have by passing in the heirarchy-path of that element (in order) to `Helpers.get_config()`. For example to get the value of `config.models.type` one would use `helpers_object.get_config('models', 'type')`.

### Adding a Config Element
To add an element, simply modify the file `Code/config.json` and add your element to whichever heirarchy you want. 

### Updating a Config Element
To update, first edit the config file and then make a call to the config reset endpoint, on a locally run server this endpoint resolves to `localhost:5000/reset_config`. This should re-load the config file. Note that this also re-starts the [Prediction Service](#prediction-service) and the [Queueing Service](#queueing-service), this means any data that was being maintained in them (in-memory) will be lost. 

## Models

There are 3 models that are available to use (others can be added easily, more on that later), I also mention how to set a few of the hyperparameters of the model by modifying `config.json` -    
  * **Touch** Uses touch duration to predict an intake. To use this model set `config.model.type = "Touch"`. Touch duration is set by `config.model.touch_threshold`. Main code file is `Code/server/touch_predictor.py`.
  * **Ensemble** Uses 4 different models to predict each action involved in pill ingestion. To use this set `config.model.type = "Ensemble"`. To decide which features to use we use `config.model.features`. `config.model.path` should specify the directory in which all 4 models are located (in .pkl format). Main code file is `Code/server/ensemble_predictor.py`
  * **Binary** Uses a single binary classifier. To use this set `config.model.type = "Binary"`. To decide which features to use we use `config.model.features`. `config.model.path` should specify the directory in which the trained model is located (in .pkl format). Main code file is `Code/server/binary_predictor.py`.

Note that even though the **Ensemble** and **Binary** models might appear very similar, they differ in one key aspect, the ground truth *labels* needed to train them. The **Ensemble** model requires ground truth to possess labels to indicate each distinct action for any sequence of sensor data, while the **Binary** model only requires a label to indicate that medication intake occured (or not) in any sequence of sensor data. This makes training them quite different even though the data they use is the same.

**FUN FACT -** Since there is no way to collect ground data for the **Ensemble** model (right now), we can't use it for the pilot! We have to use the **Binary** clf. Also since we don't have a trained **Binary** clf available right from the start, we require a model roll-out plan to train this model first. I describe it below.

### Model RollOut Plan
#### UNTESTED
A simple way we could do this is by first using the **Touch** predictor for the beginning of the pilot with a low enough touch duration value so that most touches trigger a *true* prediction from the system. This will in turn initiate a push-notification to the phone-app, which shows up in the form of a question to the user - *Did you just take xyz med?*. Whatever may be the answer to this question, we use it as ground truth. We have to use this way to ensure we are able to collect as much ground truth data as possible, thus we keep the touch duration low so that we trigger these chain of events quite frequently.  

When we believe a considerable amount of data has been collected we  do the following -  
  * We hit the training data extraction endpoint, when setup locally it resolves to the path `localhost:5000/extract_training_data`. This endpoint compiles and stores all the training data that we'll need in a *.npz* file in the directory given by `config.model.path_to_data`. 
  * You now need to use the file `Code/FeatureExtraction.py` to generate a set of *.npy* files which contain the features we need, you might need to modify the variable `path` and `datafile` to be able to use the *.npz* file we created in the previous step. I'd recommend changing the code so as to be able to accept the path as a command line argument as this would make it possible for you to run it remotely on the server machine so that the new files created/used are already available on that (physical) machine.
  * Finally, we use the file `Code/model.py` to train the model. There are a couple of hyper-parameters (stored as global variables) for this file too. Again, I would advise adding code to be able to set these params from the command line. This file will perform cross-validation by using a hold-out set, it will repeat the cross validation with randomized hold-out sets 500 times, if it's taking too long (which I believe it will when we have some non-trivial amount of data) you can reduce it, I'd still keep it around 50 if feasible.
    * `DIRECTORY` would be the directory of where the *.npz* file was kept. 
    * `TEST_SAMPLES` would be the number of samples to use for the validation set during cross validation.
    * `TRAINING_MODEL` "Binary" or "Ensemble".
    * `CLASS_TO_BE_TESTED` keep 1 for "Binary"
    * `ITERATIONS` number of iterations to use during cross-val.

After the last step, the model(s) will be stored in path `model/` as *.pkl* files. The server will pickup these models after you change the config file and reset the config. Rejoice! You're done!

## Queueing Service
This is the service class that maintains in-memory queues for every user containing their data. The main code for this is in `Code/server/Q_service.py`. This is a static class (implemented in a non-pythonic way). I would've preferred this to be a [Singleton](https://en.wikipedia.org/wiki/Singleton_pattern) or at least implemented in the [pythonic way](https://stackoverflow.com/questions/30556857/creating-a-static-class-with-no-instances) but it started off this way and I never got to changing it. This service needs to be started by making a call to `Q_service.start_service()`. I do this when the server starts up. The service is re-started each time the [config-system is refreshed](#updating-a-config-element), this causes it to lose all data from its in-memory dictionary.

The Q_service maintains an in-memory dictionary which maps each medication-ID to the sensor data (as a python list) collected so far for that medication-ID. The service has a couple of variables that it loads from the config, they are -
  * `T_WINDOW` - When the oldest data in the Queue for any medication-ID is at least `T_WINDOW` milliseconds old, then a dispatch is initiated. This means this value is in *milliseconds*.
  * `SLIDE_WINDOW` - We do not want to throw away *all* the data we dispatched, so instead we only remove the oldest `SLIDE_WINDOW` milliseconds worth of data. This means this value is in *milliseconds*.

### Enqueue
The method `Q_service.enqueue()` gets called on a different thread that is spawned by the server, this is done so that the thread responding to the `/upload_sensor_readings` request (coming from the app) does not wait on all of the fancy stuff that the Q_service and PredictionService do. This method essentially pushes the new data into the Queue corresponding to the correct Medication-ID and checks if there is enough data to perform a dispatch. To check if there is enough data, we currently only check the timestamp corresponding to the sensor `[0,0]` which is `[0-base metawear, 0-accel]`. We could check others too but I don't know if it's needed as if one sensor has seen 4-5 seconds worth of data, other sensors too must be around that mark. If you feel the samples being dispatched are too small(or big) this is the culprit!! My guess is each sensor should produce ~70-100 samples to be giving us useful information, less than ~20 means it's a cause for concern.

### Dispatch
The method `Q_service.dispatch()` gets called only if there is enough data to perform a dispatch. This method just extracts `T_WINDOW` worth of data from the queue for the given Medication-ID, wraps that data up and sends it off to the [Prediction Service](#prediction-service). The method also pops out the oldest `SLIDE_WINDOW` milliseconds worth of data, it uses basic python array indexing to do this nothing fancy.

## Prediction Service
This is the service class that performs the predictions using the predictors it also maintains the PredictionTime table. Similar to the [Queueing Service](#queueing-service), this is a static class. It also maintains an in-memory dictionary which maps Medication-ID to a tuple `(current_prediction_status, previous_yes_timestamp)`. The service has to be started by calling `PredictionService.start_service()` and this is done when the server starts up. The service is re-started each time the [config-system is refreshed](#updating-a-config-element), this causes it to lose all data from its in-memory dictionary.

The class draws a couple of global (well, *static* to be precise) variables from the config, they are -
  * `TIMEOUT_WINDOW` - The time in milliseconds after which a previous *True* prediction is considered *expired*. Any subsequent predictions (irrespective of their result) need not be made before the previous *True* prediction *expires*.
  * `CONFIRMATION_TIMEOUT` - The time in milliseconds after which a *True* prediction can be considered to be false postive (mis-classified). The system waits for a call to the endpoint `/create_intake`, which gets called when a person answer *Yes* to the question - *Did you just take a pill?*. If the system doesn't get this request or gets it after the `CONFIRMATION_TIMEOUT`, then it is considered a mis-classification, otherwise it is correct and a true positive.

The class uses a predictor that is created by the PredictorFactory according to the config element `config.model.type`. The system for adding a new predictor makes use of the [factory design pattern](https://en.wikipedia.org/wiki/Factory_method_pattern). This makes it easy to [add a new predictor](#adding-a-new-predictor) without changing code inside Prediction Service.

### Predict
The only method used by clients of the PredictionService class is the `PredictionService.predict()` method. This calls upon the predict method as implemented by the predictor object being used. In case, the prediction resolves to be *True*, then this method initiates a push notification for the app according to the `user_id` corresponding to the Medication-ID. This requires a call to `pyfcm` which needs the `push_id` of all the devices registered to this user and all of them get a push notification if things go well. The notification itself is a [*data-message*](https://firebase.google.com/docs/cloud-messaging/concept-options) that **is currently not meant to** convey information to the app, it just triggers the question *Did you just take a pill?*. Now, in case you need to know which pill is being talked about, we can send it through as the *data-message*. 

### Confirm Prediction
#### UNTESTED
The method `PredictionService.confirm_intake()` is used to record the timestamp of a *True* prediction which is also a correct prediction, in other words, the user did indeed take the pill at that exact time. This method is used to collect training data. It stores the timestamps of these true labels into the table **PredictionTimes**. This is going in **untested** because I can't test it without the complete system being in place (I could, but it would be too contrived and not indicative of the real-world at all).

### Adding a New Predictor
Make a new class and implement the abstract class `Predictor` from `Code/server/predictor.py` and make your own implementation of the method `Peredictor.predict()`, note that the data that this method accepts as input is a tuple `(sensor_data, touch_input_data)`. Touch input data is just a list of tuples `(touch_state, timestamp)`, while sensor data is a list of numpy arrays each of shape `[2-sensor_location,2-sensor_type,3-axis]`. Note that the prediction service does not get to know the timestamps corresponding to the sensor-data. I cannot remember the reason (if any) for doing this. After implementing the predict method, you need to register this new predictor class with the `PredictorFactory`, add the new predictor to the *if-else-ladder* in the `PredictorFactory.create_predictor()` method and change your config file entry `config.model.type` to use this predictor right away.

