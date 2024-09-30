import requests
import sys
import os

def download_book_cover(book_title, output_folder="book_covers"):
    # Define the base URL for the iTunes Search API
    base_url = "https://itunes.apple.com/search"

    # Set the parameters for the API request
    params = {
        "term": book_title,
        "media": "ebook",
        "limit": 1  # Only get the first result
    }

    # Make the request to the iTunes API
    response = requests.get(base_url, params=params)
    if response.status_code != 200:
        print(f"Failed to retrieve data from iTunes API: {response.status_code}")
        return

    # Parse the response JSON
    data = response.json()
    if "results" not in data or len(data["results"]) == 0:
        print(f"No book found for title '{book_title}'")
        return

    # Extract the artwork URL
    artwork_url = data["results"][0].get("artworkUrl100")
    if not artwork_url:
        print(f"No artwork found for book '{book_title}'")
        return

    # Replace '100x100' with '1200x1200' to get a higher resolution image
    high_res_artwork_url = artwork_url.replace("100x100", "1200x1200")

    # Make a request to download the high-resolution image
    image_response = requests.get(high_res_artwork_url)
    if image_response.status_code != 200:
        print(f"Failed to download high-resolution image: {image_response.status_code}")
        return

    # Create output folder if it doesn't exist
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    # Define the file path for saving the image
    file_path = os.path.join(output_folder, f"{book_title}.jpg")

    # Write the image to a file
    with open(file_path, "wb") as file:
        file.write(image_response.content)
    print(f"Downloaded high-resolution book cover for '{book_title}' to '{file_path}'")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python download_book_cover.py <book_title>")
        sys.exit(1)

    book_title = " ".join(sys.argv[1:])
    download_book_cover(book_title)
