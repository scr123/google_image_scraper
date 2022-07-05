# Google Image Scraper

Scrapes images from Google Images. User provides query, and can add additional post-processing arguments for formatting of scraped images.


## Getting Started

* Installing required script dependencies using **pip3**

  ```
  pip3 install -r requirements.txt
  ```

* Installing required script dependencies using **conda**

  ```
  conda env create -f environment.yml
  ```

## Examples

* Simple query for 10 images

  ```
  python3 scraper.py -q "your query" -t 0.5 -o /path/to/images/folder -n 10
  ```

* Query specifying .png output format

  ```
  python3 scraper.py -q "your query" -t 0.5 -o /path/to/images/folder -n 10 -f png
  ```

* Query specifying resizing of images to 256 x 256

  ```
  python3 scraper.py -q "your query" -t 0.5 -o /path/to/images/folder -n 10 -r 256 256
  ```


## Authors

* **Sean Crutchlow**

## License

This project is licensed under the MIT License - see the LICENSE file for details
