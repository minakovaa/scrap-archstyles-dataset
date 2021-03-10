from PIL import Image
from imagehash import phash
import os

# Avalible Methods in imagehash:
#
# ahash: Average hash
# phash: Perceptual hash
# dhash: Difference hash
# whash-haar: Haarwavelet hash
# whash-db4: Daubechies wavelet hash
# colorhash: HSV color hash
# crop-resistant: Crop - resistant hash


def find_similar_images(folder_path: str,
                        delete_duplicates=False):
    if not os.path.isdir(folder_path):
        return None

    hashfunc = phash

    def is_image(filename):
        f = filename.lower()
        return f.endswith(".png") or f.endswith(".jpg") or \
               f.endswith(".jpeg") or f.endswith(".bmp") or \
               f.endswith(".gif") or '.jpg' in f or f.endswith(".svg")

    image_filenames = [os.path.join(folder_path, path) for path in os.listdir(folder_path) if is_image(path)]

    list_of_removed_duplicates = []
    images = {}
    for img in sorted(image_filenames):
        try:
            hash = hashfunc(Image.open(img))
        except Exception as e:
            print('Problem:', e, 'with', img)
            continue
        if hash in images:
            # print(img, '  already exists as', ' '.join(images[hash]))
            if delete_duplicates:
                os.remove(img)
                list_of_removed_duplicates.append(img)

        images[hash] = images.get(hash, []) + [img]

    return list_of_removed_duplicates


def delete_duplicates_in_subfolders(main_folder):
    folders = os.listdir(main_folder)
    list_of_removed_duplicates = []

    for folder_path in folders:
        list_of_removed_duplicates.append(
            find_similar_images(folder_path=os.path.join(main_folder, folder_path),
                                delete_duplicates=True)
        )

    return list_of_removed_duplicates


if __name__ == '__main__':
    main_folder = os.path.join(os.getcwd(), 'scrap-arch')
    delete_duplicates_in_subfolders(main_folder)


