# Advanced Logger

A logger module with a few extra quality-of-life features not available in the base logger module.

* Fully compatible with the stdlib logging module API.
 
* Internal logging module can be swapped out easily
    * By default uses the stdlib logging module internally
    * But can use any other module compatible with the stdlib logging module

* All messages are logged as JSON


### Additional Features

* By default all messages include a metadata subfield with the logger name and time of the event

* logger.exception() Can log a message and exception stacktrace formatted as a JSON object for easier parsing in logging tools such as CloudWatch

* Log only a random sample of some messages (e.g. 1/100)
    * Useful for taking samples of production metrics

* User defined hooks allow plugging in any provided function when logging an exception

    * (usage example: save certain data about the exception to a database, send a message to a queue which should fire an email \[email/queue must be an external service\])

* Plug in any function into the is_testing argument on initialization for additional info when running in your testing setup, as well as calling any user-defined hooks.

* Remove unnecessary path info from logs except for your project's root directory
    * (example: No more "/c/user/home/projects/myApp/foo/bar.py", just get "myApp/foo/bar.py")


