# Realice

This app is a combination of create-react-app and AWS Chalice in order to create an instant serverless project.

## Prerequisites

Before beginning, make sure you have Node 8.10.0 or later on your machine. This is so the app can call the command, npx create-react-app.

Also make sure you have the AWS profile you wish to use enabled on your computer.

## Installation

Simply install the requirements.txt file using pip/pip3 install -r

## Getting started

This app leverages the python library invoke. Call the following to start your app.

```
invoke initialize
```

Enter your app name and Realice will do the rest.

To get a list of commands run

```
invoke --list
```

If you plan to use the default API URL for your app, be sure to enable CORS in your api like so:

```
@app.route('/', **cors=True**)
```

## Built with

* [Facebook create-react-app](https://github.com/facebook/create-react-app)
* [AWS Chalice](https://github.com/aws/chalice)

## Authors

* **Luke Household** - [LHousehold](https://github.com/LHousehold)

## License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details
