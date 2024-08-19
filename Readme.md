# Google Calendar Integration Setup

![Icon](./bandecocalendar.png)

## Prerequisites

Before starting, ensure you have the following:

1. **Google Calendars**: Create the calendars you wish to integrate.
2. **Google Cloud Account**: Access to the Google Cloud Console to create a service account.
3. **Google Cloud SDK**: Installed on your machine.

## Setup Instructions

### 1. Create Google Calendars

- Create the required calendars in Google Calendar.
- Go to the settings of each calendar, click on the "Integrate calendar" tab, and find the **Calendar ID**.
- Copy the Calendar ID and paste it into a file named `IDs.txt` in the root directory of this repository. The file should look like this:

    ```text
    calendar1IDFORNORMALMEALS
    calendar2IDFORVEGANMEALS
    ```

### 2. Set Up a Google Cloud Service Account

- You need a service account to allow the application to interact with your Google Calendar.
- Follow the instructions [here](https://cloud.google.com/iam/docs/creating-managing-service-accounts) to create a service account in the Google Cloud Console.
- After creating the service account, create a key for it.

### 3. Install Google Cloud SDK

- To create the service account key, you will need to install the Google Cloud SDK. Instructions for installation can be found [here](https://cloud.google.com/sdk/docs/install-sdk).
- Once the SDK is installed, you can generate a key for your service account using the following command:

    ```bash
    gcloud iam service-accounts keys create key.json --iam-account=SERVICE_ACCOUNT_EMAIL
    ```

    Replace `SERVICE_ACCOUNT_EMAIL` with the email address of your service account.

### 4. Share Your Calendars with the Service Account

- To allow the service account to access your calendars, you need to share the calendars with it.
- Go to the settings of the calendar you want to share, and click on the "Share with specific people" tab.
- Add the email of the service account and give it the necessary permissions (typically "Make changes to events").
- You can find the service account's email address in the Google Cloud Console under the "Service accounts" tab.

### 5. Configure the Application

- Place the `key.json` file (the service account key) in the root directory of this repository.
- Ensure that the `IDs.txt` file containing your calendar IDs is also in the root directory.

### 6. Install Dependencies

- Before running the application, make sure you have installed all necessary dependencies. You can do this using pip:

    ```bash
    pip install -r requirements.txt
    ```

### 7. Run the Application

- Now that everything is set up, you can run the application. Depending on the application's design, you might need to run a specific script or start a service.
- For example:

    ```bash
    python3 bandecoCalendar/calendar_funcs.py
    ```

- The application should now be able to access the specified Google Calendars and perform the intended operations.

## Additional Notes

- **Security Considerations**: Ensure that your `key.json` file is kept secure. Do not commit this file to version control systems like GitHub. Add `key.json` to your `.gitignore` file to avoid accidentally pushing it to a public repository.
- **Error Handling**: If the application encounters issues accessing the calendars, double-check that the calendar IDs are correct and that the service account has been granted the necessary permissions.
- **Further Customization**: Depending on your needs, you might want to customize the application's behavior or add more calendars to the `IDs.txt` file.

## Troubleshooting

- **Permission Errors**: If you receive errors related to permissions, make sure that the service account has been correctly added to the calendars with the appropriate permissions.
- **Authentication Issues**: If there are issues with the service account authentication, verify that the `key.json` file is correctly placed in the root directory and that the path to this file is correctly referenced in the code.


## Current Menu

<iframe src="https://calendar.google.com/calendar/embed?height=600&wkst=1&ctz=America%2FRecife&bgcolor=%23ffffff&mode=WEEK&src=ZGRlODJjZGJmYjgwNmY3NzlkNWZiYzJiZWRkZjQ1YmMxNDBiYTQzYTQzZDI2NDQ2OWQ0MjU1OGNlMzkzMjY5N0Bncm91cC5jYWxlbmRhci5nb29nbGUuY29t&src=YzczOTA2NTJjYmU2ZTA1ZmY5NzhiOTcwODdhYmIzNWE0N2VjMjU4NGEzODkxNmViZDE5ZDg0Mjg4NDA0ZTUyM0Bncm91cC5jYWxlbmRhci5nb29nbGUuY29t&color=%233F51B5&color=%23795548" style="border:solid 1px #777" width="800" height="600" frameborder="0" scrolling="no"></iframe>

## Add Bandeco Menu to your calendar

- **Padrão**: [Click to add to your agenda](https://calendar.google.com/calendar/u/1?cid=ZGRlODJjZGJmYjgwNmY3NzlkNWZiYzJiZWRkZjQ1YmMxNDBiYTQzYTQzZDI2NDQ2OWQ0MjU1OGNlMzkzMjY5N0Bncm91cC5jYWxlbmRhci5nb29nbGUuY29t)
- **Vegano**: [Click to add to your agenda](https://calendar.google.com/calendar/u/1?cid=YzczOTA2NTJjYmU2ZTA1ZmY5NzhiOTcwODdhYmIzNWE0N2VjMjU4NGEzODkxNmViZDE5ZDg0Mjg4NDA0ZTUyM0Bncm91cC5jYWxlbmRhci5nb29nbGUuY29t)