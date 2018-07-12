import os
import boto3
import botocore

stored_data_dir = '/home/ubuntu/projects/crawling/store/img_progress.txt'
def get_file_from_bucket(files, save_dir, key_dir='raw/'):
    print(files)
    print(save_dir)
    BUCKET_NAME = 'avagaistyle'
    s3 = boto3.resource('s3')
    imgids = []
    with open(stored_data_dir, 'r') as f:
        stored = [line.strip() for line in f.readlines()]
        for file in files:
            mall = file.split('_')[0]
            color = file.split('_')[-1]
            id = '_'.join(file.split('_')[2:-1])
            fetch_id = '{}-{}-{}-'.format(mall, id, color)
            for s in stored:
                if fetch_id in s:
                    imgids.append(s)

    for img in imgids:
        KEY = '{}{}'.format(key_dir, img)

        try:
            s3.Bucket(BUCKET_NAME).download_file(KEY, os.path.join(save_dir, img))
            print('Image {} fetched'.format(KEY))
        except botocore.exceptions.ClientError as e:
            if e.response['Error']['Code'] == "404":
                print("The object does not exist.")
                continue
            else:
                print("Other problem")
                continue
