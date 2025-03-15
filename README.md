# GLNW – Local Goods Marketplace

## Description
GLNW is a cutting-edge web-based marketplace designed to bridge the gap between buyers and sellers within North Wales. The platform allows users to register as either **buyers** or **sellers**, facilitating the process of listing products and searching for items within a specified geographic range. By leveraging postcode distance calculations, GLNW ensures that users can efficiently find local products, making it a valuable tool for community-driven commerce.

Whether you are looking to declutter your home by selling unused items or searching for great deals on local products, GLNW has got you covered. The platform’s user-friendly interface and powerful features make buying and selling effortless and enjoyable.

## Video Demo
Experience GLNW in action by watching our video demonstration:  
[GLNW Video Demo](https://www.youtube.com/watch?v=rzB0Cd1R-0Y)

The video walkthrough highlights how to set up your profile, list items, and perform distance-based searches with ease. See how the interactive map and search functionalities simplify the buying and selling experience within the North Wales area.

## Features
GLNW comes equipped with a wide range of features designed to optimize local trading and enhance user experience:

- **User Authentication** – Secure and reliable login and registration system to protect user data.
- **Distance-Based Search** – Advanced search functionality that calculates proximity using postcode data to help users find sellers nearby.
- **Product Listings** – Straightforward product listing interface for sellers to add, update, and manage items efficiently.
- **Contact Sellers** – Seamless communication by displaying seller emails for direct inquiries, making transactions quicker and more personal.
- **Responsive UI** – Modern, clean, and mobile-friendly design, powered by Bootstrap to ensure a consistent experience on all devices.

## Tech Stack
GLNW is built with modern web technologies to ensure performance, security, and scalability:

- **Backend**: Flask (Python), SQLite for efficient database management, and Google Maps API for geographical data handling.
- **Frontend**: HTML and CSS (leveraging Bootstrap for responsive design) alongside JavaScript for dynamic content and interactivity.
- **APIs**: Integration with Postcodes.io for postcode validation and the Google Geocoding API to convert addresses into geographic coordinates.

## Installation
Setting up GLNW is quick and straightforward. Follow these steps to get your local instance running:

1. **Clone the repository**  
   ```bash
   git clone https://github.com/yourusername/glnw.git
   cd glnw
   ```

2. **Set up a virtual environment**  
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```
   *(On Windows, use `venv\Scripts\activate`)*

3. **Install dependencies**  
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up the database**  
   ```bash
   sqlite3 glnw.db < schema.sql
   ```

5. **Run the application**  
   ```bash
   flask run
   ```

## Configuration
To properly configure the application, make sure to set your **Google Maps API Key** in `app.py` as follows:

```python
GOOGLE_MAPS_API_KEY = "your_api_key_here"
```

Additionally, ensure that **Flask-Session** is installed to manage user sessions efficiently.

## Troubleshooting
Here are some common issues and solutions to help you troubleshoot potential problems:

- **No results appearing?** Double-check the validity of your Google API key and make sure it is correctly set in the configuration file.
- **Distance always showing as 0km?** Verify that postcodes are entered correctly and that API calls are successfully retrieving data.
- **Login/Register not working?** Restart the Flask application and clear any stored session data to resolve potential conflicts.

## Contributions
We welcome contributions from the community! Feel free to fork the repository, submit pull requests, or report issues on our GitHub page. Help us enhance GLNW and make it even better for users across North Wales.

## License
This project is licensed under the MIT License. See the LICENSE file for more details.

## Author
Developed and maintained by [Matt Holmes](https://github.com/mattholmescodes).

