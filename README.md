# scrap-archstyles-dataset
Scrap images from google.com and yandex.ru for make dataset of several arch styles in Moscow.

Scrap for achstyles:
 - модерн,
 - модернизм,
 - хайтек,
 - классицизм,
 - неоготика,
 - неоренессанс.
 

Scrapping programm in file `scrap_images.py` use chromedriver and scrap images from yandex.ru and google.com. 
Big thx Anand Suresh for some code from [this post](https://medium.com/@wwwanandsuresh/web-scraping-images-from-google-9084545808a2).

After scrapping you should delete duplicate images with code frome `find_similar_imgs.py`

All code with scrappin images and delete duplicates after it you can run in `main_scrap_arch_dataset.py`.


