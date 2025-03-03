> project_name/
        ├── package_one/
        │   ├── pyproject.toml
        │   └── src/
        │       └── package_one/
        │           └── __init__.py
        ├── package_two/
        │   ├── pyproject.toml
        │   └── src/
        │       └── package_two/
        │           └── __init__.py
        └── shared_module/
            ├── pyproject.toml
            └── src/
                └── shared_module/
                    └── __init__.py


# install mongodb
# sudo apt install -y mongodb-org
# echo "deb http://security.ubuntu.com/ubuntu impish-security main" | sudo tee /etc/apt/sources.list.d/impish-security.list# sudo apt-get update
# sudo apt-get install libssl1.1
# wget -qO - https://www.mongodb.org/static/pgp/server-7.0.asc | sudo gpg --dearmor -o /usr/share/keyrings/mongodb-server-7.0.gpg
# echo "deb [ arch=amd64,arm64 signed-by=/usr/share/keyrings/mongodb-server-7.0.gpg ] https://repo.mongodb.org/apt/ubuntu jammy/mongodb-org/7.0 multiverse" | sudo tee /etc/apt/sources.list.d/mongodb-org-7.0.list
# sudo apt update
# sudo apt install -y mongodb-org
