from scrap_images import download_img_by_search_query, YANDEX_IMG, GOOGLE_IMG
from find_similar_imgs import find_similar_images, delete_duplicates_in_subfolders
import os
import asyncio


def scrap_images_of_arch_styles(dataset_folder: str, number_of_each_query: int = 100):
    # Enter your path where you would like to save images
    images_path = os.path.join(os.getcwd(), dataset_folder)

    # Change your list of querries here
    queries = ['модерн',
               'модернизм -модерн',  # except 'модерн', because queries are similar
               'хайтек',
               'классицизм',
               'неоготика',
               'неоренессанс']

    queries = ['архитектура москва {0}'.format(query) for query in queries]

    # You must define subfolders for each query by first word in query
    subfolders_for_queries = [q.split()[2] for q in queries]

    for search_engine in [YANDEX_IMG, GOOGLE_IMG]:
        asyncio.run(download_img_by_search_query(queries, number_of_each_query, images_path,
                                                 search_engine=search_engine,
                                                 is_headless=False,
                                                 subfolders_for_queries=subfolders_for_queries)
                    )


if __name__ == '__main__':
    dataset_folder = 'scrap-arch'
    # Enter number of img of each query would you like
    number_of_each_query = 50

    # scrap images of buildings of several arch styles
    scrap_images_of_arch_styles(dataset_folder, number_of_each_query)

    # delete duplicates from scrapped images
    main_folder = os.path.join(os.getcwd(), dataset_folder)
    delete_duplicates_in_subfolders(main_folder)
