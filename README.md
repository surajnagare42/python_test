# Project Setup and Execution Guide

To run this project, follow the steps outlined below. Ensure that Docker is installed on your system before proceeding. If Docker is not installed, you can download and install it from internet.

## Requirements:

Docker version >= 3

**Note**: This project utilizes the free version of https://manage.exchangeratesapi.io/, which has limitations on the number of API calls. Therefore, the project is configured to fetch a limited amount of data. If you have a premium API key or need to adjust the date range, follow the instructions below.

### Update Environment Variables:

Open the .env file and update the START_DATE and END_DATE to the desired date range.
Example:

makefile
Copy code
START_DATE=2022-01-01
END_DATE=2022-01-10

### Building Docker Image:

Open a terminal window.
Navigate to the project directory.
Run the following command to build the Docker image:
``` bash
sudo docker-compose build 
```
### Running the Project:

After the image is built successfully, run the project using the following command:
```bash
docker-compose up
```
This command will start the project and execute the necessary tasks, including making API calls, processing data, and storing it in the database.

### Customization (Optional):

If you have a premium API key or need to adjust any other settings, you can update the .env file or modify the code as needed.
For any changes to the code or environment variables, repeat steps 2 and 3 to rebuild and run the project.
By following these steps, you can successfully set up and run the project in your Docker environment. If you encounter any issues or need further assistance, feel free to reach out for support.