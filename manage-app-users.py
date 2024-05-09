import argparse
import boto3

parser = argparse.ArgumentParser(description='Create Bookstore App Users in Amazon Cognito')
parser.add_argument('--command', required=True, help='Command to run - either `create` or `delete`')
parser.add_argument('--cognito-user-pool-id', required=True, help='Cognito User Pool ID')
parser.add_argument('--email-prefix', help='Part of the email before @')
parser.add_argument('--email-postfix', help='Email domain without @')
parser.add_argument('--password', default='Test!123', help='Password for created users')

args = parser.parse_args()

command = args.command
cognito_user_pool_id = args.cognito_user_pool_id
email_prefix = args.email_prefix
email_postfix = args.email_postfix
password = args.password

USERS = [
    {
        'username': 'Tom',
        'email_part': '+tom',
        'group': 'Admins',
        'yearsAsMember': '10',
    },
    {
        'username': 'Frank',
        'email_part': '+frank',
        'group': 'Admins',
        'yearsAsMember': '1',
    },
    {
        'username': 'Dante',
        'email_part': '+dante',
        'group': 'Publishers',
        'yearsAsMember': '5',
    },
    {
        'username': 'William',
        'email_part': '+william',
        'group': 'Publishers',
        'yearsAsMember': '1',
    },
    {
        'username': 'Andrew',
        'email_part': '+andrew',
        'group': 'Customers',
        'yearsAsMember': '3',
    },
    {
        'username': 'Susan',
        'email_part': '+susan',
        'group': 'Customers',
        'yearsAsMember': '1',
    },
    {
        'username': 'Toby',
        'email_part': '+toby',
        'group': 'Customers',
        'yearsAsMember': '2',
    },
]

cognito_client = boto3.client('cognito-idp')

if command == 'create':
    if not email_prefix:
        raise Exception('Email prefix is required for creating users')
    if not email_postfix:
        raise Exception('Email postfix is required for creating users')
    if not password:
        raise Exception('Password is required for creating users')

for user in USERS:
    if command == 'delete':
        cognito_client.admin_delete_user(
            UserPoolId=cognito_user_pool_id,
            Username=user['username']
        )

        print(f'Deleted user: {user["username"]}')
    elif command == 'create':
        cognito_client.admin_create_user(
            UserPoolId=cognito_user_pool_id,
            Username=user['username'],
            UserAttributes=[
                {
                    'Name': 'email',
                    'Value': f'{email_prefix}{user["email_part"]}@{email_postfix}'
                },
                {
                    'Name': 'email_verified',
                    'Value': 'true'
                },
                {
                    'Name': 'custom:role',
                    'Value': user['group']
                },
                {
                    'Name': 'custom:yearsAsMember',
                    'Value': user['yearsAsMember']
                }
            ],
            TemporaryPassword=password,
            MessageAction='SUPPRESS'
        )

        print(f'Created user: {user["username"]}')

        cognito_client.admin_set_user_password(
            UserPoolId=cognito_user_pool_id,
            Username=user['username'],
            Password=password,
            Permanent=True
        )

        print(f'Set password for user: {user["username"]}')

        cognito_client.admin_add_user_to_group(
            UserPoolId=cognito_user_pool_id,
            Username=user['username'],
            GroupName=user['group']
        )

        print(f'Added user: {user["username"]} to group {user["group"]}')
