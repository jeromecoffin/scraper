# Luxury Price Scraper

This project is a Python-based web scraper designed to extract price information from a specific set of URLs, log the results, and store them in a TinyFlux database. The scraper is configured to run in a Docker container and uses Selenium for web interactions.

## Table of Contents
- [Installation](#installation)
- [Environment Variables](#environment-variables)
- [Usage](#usage)
- [Logging](#logging)
- [Database](#database)
- [Notes](#notes)
- [License](#license)

## Installation

### Prerequisites
1. **Docker:** Ensure Docker is installed on your system.
2. **Python Dependencies:** The script requires certain Python packages, which are usually included in the Docker image.

### Build and Run Docker Container

1. Clone this repository:

    ```bash
    git clone https://github.com/jeromecoffin/scraper.git
    cd scraper
    ```

2. Build the Docker image:

    ```bash
    docker build -t scraper .
    ```

3. Run the Docker container:

    ```bash
    docker run -v /path/to/data:/app/data --env-file vraiables/ scraper
    ```

   Replace `/path/to/data` with the path to the directory where you want to store logs and the TinyFlux database. Ensure `.env` file is properly configured.

## Environment Variables

The scraper relies on several environment variables for its configuration. It was initialy deployed on gitlab. Please check .gitlab-ci.yml. These variables can be set in the varaible file:

```bash
BASE_URL="https://www.example.com/product/"
COOKIES_XPATH="//button[@id='accept-cookies']"
PRICE_XPATH="//span[@class='price']"
NUM_LINES_TO_READ=100
LIST_REFERENCES="/app/data/list_references.txt"
CONTAINER_NAME="container_1"
```

- `BASE_URL`: The base URL for the target website.
- `COOKIES_XPATH`: XPath for the "Accept Cookies" button.
- `PRICE_XPATH`: XPath for the price element on the webpage.
- `NUM_LINES_TO_READ`: Number of lines to read from the `LIST_REFERENCES` file.
- `LIST_REFERENCES`: Path to the file containing a list of references to append to the `BASE_URL`.
- `CONTAINER_NAME`: Unique name for the container, used in generating log and database file names.

## Usage

Once the container is running, the script will:
1. Open the `LIST_REFERENCES` file and read a subset of lines based on the container's index.
2. For each reference, append it to the `BASE_URL` and navigate to the page.
3. Accept cookies if the banner is present.
4. Scrape the price from the page and store it in a TinyFlux database.
5. Log each operation and any errors encountered.

## Logging

Logs are stored in a file located at `/app/data/logs/log_<CONTAINER_NAME>.txt`. The log includes:
- URLs accessed.
- Prices extracted.
- Errors encountered (e.g., elements not found, invalid price formats).

## Database

The scraped data is stored in a TinyFlux database located at `/app/data/<CONTAINER_NAME>.db`. Each price entry is recorded with the following structure:
- `time`: Timestamp of the scrape.
- `measurement`: Always "price".
- `tags`: Includes `bag` (reference) and `zone` (currency zone, here "euro").
- `fields`: Contains the `count`, which is the numeric price.

## Notes

- Ensure that the `chrome_driver_binary` and `binary_location` paths in the script are correct for your environment.
- The script uses a headless Chrome browser for scraping to minimize resource usage.
- Sleep intervals are added to ensure elements have enough time to load before interaction.

## License

This project is licensed under the MIT License. See the `LICENSE` file for details.

---

Feel free to customize any part of the above ReadMe according to the specific needs or additional features of your project. Let me know if you have any other questions!
