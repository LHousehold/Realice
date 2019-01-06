from invoke import task, run
from os import path
import boto3
import configparser
import webbrowser


@task
def initialize(ctx):
    if path.isfile('config.ini'):
        print('Project has already been initialized. Returning...')
        return
    app_name = input("Please enter a name for your app: ")
    aws_profile = input("Please provide the AWS Profile you wish to use (press enter for default): ") or 'default'
    aws_region = input("Please provide the AWS Region you wish to use: ")
    ctx.run(f'npx create-react-app ui-{app_name}')
    ctx.run(f'chalice new-project api-{app_name}')
    createConfigFile(ctx, app_name, aws_profile, aws_region)

@task
def createConfigFile(ctx, app_name, aws_profile, aws_region):
    if aws_region:
        session = boto3.Session(profile_name=aws_profile, region_name=aws_region)
    else:
        session = boto3.Session(profile_name=aws_profile)

    bucket_name = app_name.lower() + "-bucket"
    static_url = 'http://' + bucket_name + '.s3-website.' + session.region_name + '.amazonaws.com'

    config = configparser.ConfigParser()
    config.add_section('ProjectConfiguration')
    config.set('ProjectConfiguration', 'name', app_name)
    config.set('ProjectConfiguration', 'bucketName', bucket_name)
    config.set('ProjectConfiguration', 'uiUrl', static_url)
    config.set('ProjectConfiguration', 'uiDirectory', f'ui-{app_name}')
    config.set('ProjectConfiguration', 'apiDirectory', f'api-{app_name}')
    config.set('ProjectConfiguration', 'awsProfile', aws_profile)
    config.set('ProjectConfiguration', 'awsRegion', aws_region)
    
    with open('config.ini', 'w') as config_file:
        config.write(config_file)

@task
def createHostBucket(ctx):
    config = getConfig()
    bucket_name = config.get('bucketName')
    aws_region = config.get('awsRegion')

    print('Creating host bucket ' + bucket_name)

    s3 = boto3.client('s3')

    s3.create_bucket(
        Bucket=bucket_name,
        CreateBucketConfiguration={
            'LocationConstraint': aws_region
        }
    )

    website_configuration = {
        'IndexDocument': {'Suffix': 'index.html'}
    }

    s3.put_bucket_website(
        Bucket=bucket_name,
        WebsiteConfiguration=website_configuration
    )

    s3.get_bucket_website(
        Bucket=bucket_name
    )

@task
def deployUi(ctx):
    config = getConfig()
    bucket_name = config.get('bucketName')
    ui_directory = config.get('uiDirectory')
    try:
        run(f'aws s3 sync {ui_directory}/build s3://' + bucket_name + '/ --acl public-read')
    except Exception as e:
        print('Check that you have run createHostBucket and that the build directory exists inside the ui directory')

@task
def buildUi(ctx):
    ui_directory = getConfig().get('uiDirectory')
    with ctx.cd(ui_directory):
        ctx.run('npm run build')

@task
def cleanUi(ctx):
    ui_directory = getConfig().get('uiDirectory')
    with ctx.cd(ui_directory):
        print('Cleaning ui\n')
        ctx.run('rm -rf build')

@task
def deployApi(ctx):
    config = getConfig()
    api_directory = config.get('apiDirectory')
    with ctx.cd(api_directory):
        result = ctx.run('chalice deploy')
        for line in result.stdout.splitlines():
            if line.startswith('  - Rest API URL: '):
                api_url = line.split('  - Rest API URL: ')[1].strip()
                if api_url:
                    writeConfig('apiUrl', api_url)

@task
def ui(ctx):
    static_url = getConfig().get('uiUrl')
    print(f'Public URL: {static_url}')

def getConfig():
    config = configparser.ConfigParser()
    config.read('config.ini')
    return config['ProjectConfiguration']

def writeConfig(key, value):
    config = configparser.ConfigParser()
    config.read('config.ini')
    config.set('ProjectConfiguration', key, value)
    with open('config.ini', 'w') as config_file:
        config.write(config_file)
