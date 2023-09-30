# Admin Dashboard using FastAPI and Tailwind CSS

This project provides a way to serve admin/analytical dashboards using FastAPI and Tailwind CSS based on the Django admin format.

## Running locally
- Create a virtual environment and install the requirements using the commands:
```
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```
- Start the server using the command:
```
uvicorn api:app
```

## Customization

The project provides a basic layout for the admin dashboard. You can customize the layout by modifying the HTML templates in the templates directory. You can also modify the CSS styles by modifying the files in the static/css directory.

## Contributing

Contributions are welcome! If you find any bugs or have any suggestions for improvement, please open an issue or submit a pull request.