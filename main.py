from fastapi import FastAPI
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from fastapi.responses import JSONResponse
from bs4 import BeautifulSoup

app = FastAPI()

# Configure Selenium WebDriver
def get_selenium_driver():
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")

    # Set the path to the Chrome binary explicitly
    chrome_options.binary_location = "/usr/bin/google-chrome"  # Path to your installed Google Chrome

    # Specify the path to the downloaded chromedriver
    chrome_driver_path = "./chromedriver-linux64/chromedriver"  # Update this path
    
    # Create the driver using the specified chromedriver and options
    driver = webdriver.Chrome(service=Service(chrome_driver_path), options=chrome_options)
    return driver

@app.get("/scrape")
async def scrape():
    # URL to scrape directly
    url = "https://www.scrapethissite.com/pages/forms/"

    # Initialize the Selenium WebDriver
    driver = get_selenium_driver()

    try:
        # Open the URL
        driver.get(url)

        # Get the raw HTML of the page
        page_html = driver.page_source

        # Parse the page HTML with BeautifulSoup
        soup = BeautifulSoup(page_html, 'html.parser')

        # Find the table with class 'table'
        table = soup.find('table', class_='table')

        # Extract the data from the table rows <tr class="team">
        table_data = []
        rows = table.find_all('tr', class_='team')

        for row in rows:
            # Extract the columns from each row
            columns = row.find_all('td')
            
            # Ensure the row contains the expected number of columns
            if len(columns) == 9:
                team_name = columns[0].text.strip()
                year = columns[1].text.strip()
                wins = columns[2].text.strip()
                losses = columns[3].text.strip()
                ot_losses = columns[4].text.strip()
                pct = columns[5].text.strip()
                gf = columns[6].text.strip()
                ga = columns[7].text.strip()
                diff = columns[8].text.strip()

                # Append the extracted data to the list
                table_data.append({
                    "team_name": team_name,
                    "year": year,
                    "wins": wins,
                    "losses": losses,
                    "ot_losses": ot_losses,
                    "pct": pct,
                    "gf": gf,
                    "ga": ga,
                    "diff": diff
                })

        # Return the scraped data as JSON
        return JSONResponse(content={"data": table_data})

    finally:
        driver.quit()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)
