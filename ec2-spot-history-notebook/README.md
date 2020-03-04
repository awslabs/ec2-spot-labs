# Spot Historic Price Notebook 

The content in this folder uses [CDK](https://docs.aws.amazon.com/cdk/latest/guide/home.html) to deploy the infrastructure, IAM roles and policies required to run a [Sagemaker Notebook](https://docs.aws.amazon.com/sagemaker/latest/dg/notebooks.html) ready to fetch and display EC2 Spot historic prices using a Jupyter notebook. You can see how that notebook looks like [here](./ec2-spot-historic-prices.ipynb). 

## Deploying CDK project using Cloud9   
The easier way to setup and deploy your environment is using Cloud9 following this instructions:

* Create a Cloud9 environment : 
* On the console run the following commands:

```
npm install -g --force aws-cdk
pip install virtualenv
git clone https://github.com/awslabs/ec2-spot-labs.git
cd $HOME/environment/ec2-spot-labs/ec2-spot-history-notebook/cdk
virtualenv .env
source .env/bin/activate
pip install -r requirements.txt 
cdk deploy
```

## Setting up the project with CDK

To execute this project, you just need to follow the usual steps required to work with CDK projects. You can follow the [CDK Getting Started](https://docs.aws.amazon.com/cdk/latest/guide/getting_started.html) page content, install node/npm and aws cdk.

The `cdk.json` file tells the CDK Toolkit how to execute your app.

This project is set up like a standard Python project.  There is also a `.env` virtualenv directory.  To create the virtualenv it assumes that there is a `python3` (or `python` for Windows) executable in your path with access to the `venv` package. If for any reason the automatic creation of the virtualenv fails, you can create the virtualenv manually.

To manually create a virtualenv on MacOS and Linux:

```
$ python3 -m venv .env
```

After the init process completes and the virtualenv is created, you can use the following step to activate your virtualenv.

```
$ source .env/bin/activate
```

If you are a Windows platform, you would activate the virtualenv like this:

```
% .env\Scripts\activate.bat
```

Once the virtualenv is activated, you can install the required dependencies.

```
$ pip install -r requirements.txt
```

At this point you can now synthesize the CloudFormation template for this code.

```
$ cdk synth
```

Finally to drive the installation of the presentation

```
$ cdk deploy
```


## Useful commands
Other useful `cdk` commands:

 * `cdk ls`          list all stacks in the app
 * `cdk synth`       emits the synthesized CloudFormation template
 * `cdk deploy`      deploy this stack to your default AWS account/region
 * `cdk diff`        compare deployed stack with current state
 * `cdk docs`        open CDK documentation


### Things to note

#### Changing the profile used to create the account.

By default CDK will use the default profile. To change the profile use the following command 
before executing any of the `cdk` commands.

```
$ export AWS_PROFILE=my_profile
```

#### Changing the github repository url

By default the URL points to [https://github.com/awslabs/ec2-spot-labs.git](https://github.com/awslabs/ec2-spot-labs.git)
You can modify the default repository to load by executing the following command 
before executing any of the `cdk` commands. This might be useful for example when working on Pull requests.

```
$ export AWS_SPOT_REPO="https://github.com/ruecarlo/ec2-spot-labs.git"
```

This will change the configuration to load the right repository.
