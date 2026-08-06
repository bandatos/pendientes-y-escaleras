
import csv
from datetime import datetime
from typing import Any, Dict, List

from django.conf import settings
from report.models import EvidenceImage


class CleanBucket:
    my_bucket: Any
    files_models_in_db: Dict[str, List] = {}
    files_in_s3: List = []
    files_in_db: List = []
    dict_files_in_db: Dict[str, int] = {}
    orphans: List = []
    responses: List = []
    in_s3_by_csv: bool = False
    global_aws_location = f"{getattr(settings, 'AWS_MEDIA_LOCATION', '')}/"

    def __init__(
            self, aws_location="", limit=10000, exclude_recent=False,
            run=True, only_imss=False, in_s3_by_csv=True):
        import boto3
        from django.conf import settings
        # from scripts.common import build_s3
        # from task.aws.common import BotoUtils

        bucket_name = getattr(settings, "AWS_STORAGE_BUCKET_NAME")
        aws_access_key_id = getattr(settings, "AWS_ACCESS_KEY_ID")
        aws_secret_access_key = getattr(settings, "AWS_SECRET_ACCESS_KEY")
        s3 = boto3.resource(
            's3', aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key)
        self.my_bucket = s3.Bucket(bucket_name)
        if "escaleras/" in aws_location:
            self.aws_location = aws_location
        # else:
        #     self.aws_location = "data_files/"
        # self.aws_location = aws_location or self.aws_location
        self.excluded_dirs = []
        # "admin/", "aws_errors/", "cat_images/", "catalogs/", "ckeditor/",
        # "data_samples/", "experiment/", "image_rx/", "logos/",
        # "mat_views/", "profile_images/", "rest_framework/",
        # "sheet_samples/", "catalog/", "localhost/",]
        recent_dirs = []
        # "month_tables/", "reply/", "data/", "sheet/", "table/",
        # "merged_tables/",]
        self.include_dirs = []
        if not exclude_recent:
            self.excluded_dirs += recent_dirs
            if not self.aws_location:
                self.include_dirs = ["nacional/", "estatal/", "hospital/"]
        # self.s3_utils = BotoUtils(build_s3())
        self.storage_name = "GLACIER_IR"
        self.run = run
        self.only_imss = only_imss
        self.report = {
            "new_data_files": 0,
            "new_sheet_files": 0,
            "already_exist": 0,
            "clone_saved": 0,
        }
        self.in_s3_by_csv = in_s3_by_csv

    def __call__(self):
        self.get_files_in_db()
        self.get_files_in_s3()
        self.find_orphans()
        print("Orphans found: ", datetime.now().strftime("%H:%M:%S"))
        self.report_orphans()

    def get_files_in_db(self):
        print("Getting files in db: ", datetime.now().strftime("%H:%M:%S"))
        model_files = [EvidenceImage]
        for model in model_files:
            self.get_files_in_model(model)
        # self.files_in_db = list(set(self.files_in_db))
        for file in self.files_in_db:
            self.dict_files_in_db.setdefault(file, 0)
            self.dict_files_in_db[file] += 1

    def get_files_in_model(self, model):
        model_file_query = model.objects.filter(image__isnull=False)
        model_count = model_file_query.count()
        for i in range(0, model_count, 1000):
            self.files_in_db.extend(
                model_file_query.values_list('image', flat=True)[i:i+1000])

    def _get_s3_with_list_objects(self):
        if self.include_dirs:
            all_bucket_files = []
            for included_dir in self.include_dirs:
                all_bucket_files += self.my_bucket.objects.filter(
                    Prefix=f"{self.global_aws_location}{included_dir}")
        else:
            all_bucket_files = self.my_bucket.objects.filter(
                Prefix=self.aws_location)

        for bucket_obj in all_bucket_files:
            bucket_obj_key = bucket_obj.key.replace(
                self.global_aws_location, '')
            if any(
                    bucket_obj_key.startswith(excluded_dir)
                    for excluded_dir in self.excluded_dirs
            ):
                continue
            self.files_in_s3.append((bucket_obj_key, bucket_obj.size))

    def get_files_in_s3(self):
        from urllib.parse import unquote
        self.files_in_s3 = []

        print("Getting files in s3: ", datetime.now().strftime("%H:%M:%S"))

        if not self.in_s3_by_csv:
            return self._get_s3_with_list_objects()

        csv_file_path = getattr(settings, "FILES_IN_S3_CSV_FILE_PATH")
        try:
            with open(csv_file_path, mode='r') as file:
                reader = csv.reader(file)
                # data_files/estatal/ichihs/080140423000144/2%20Surtido.xlsx_SHEET_Sheet%201.csv
                lines = [row for row in reader]
        except FileNotFoundError:
            print("No se encontro el archivo csv")
            return

        for line in lines:
            line_count = len(line)
            bucket_obj_key = line[1] if line_count > 1 else ""
            bucket_obj_size = line[2] if line_count > 2 else 0
            bucket_obj_key = unquote(bucket_obj_key)
            if not bucket_obj_key or not isinstance(bucket_obj_key, str):
                continue

            bucket_obj_key = bucket_obj_key.replace(self.global_aws_location, '')

            if any(
                bucket_obj_key.startswith(excluded_dir)
                for excluded_dir in self.excluded_dirs
            ):
                continue

            self.files_in_s3.append((bucket_obj_key, bucket_obj_size))

    def find_orphans(self):
        print("Finding orphans: ", datetime.now().strftime("%H:%M:%S"))
        files_in_db = set(self.files_in_db)
        self.orphans = [
            (file, size) for file, size in self.files_in_s3
            if file not in files_in_db
        ]

    def report_orphans(self):
        total_size = sum(size for _, size in self.orphans)
        print("Total files in db: ", len(self.files_in_db))
        print("Total files in s3: ", len(self.files_in_s3))
        s3_size = sum(size for _, size in self.files_in_s3)
        s3_size = s3_size / (1024 * 1024)
        s3_size = round(s3_size, 2)
        print("Total size of files in s3: ", s3_size, "MB")
        print(f"Total orphans: {len(self.orphans)}")
        print(f"Total size of orphans: {total_size} bytes")
        print(f"Total size of orphans: {total_size/(1024*1024)} MB")

    def clean_orphans(self, delete_lote=1000):
        self.responses = delete_files(
            self.orphans, self.my_bucket, delete_lote)


def delete_files(files, s3_bucket=None, delete_lote=1000):
    from django.conf import settings
    responses = []
    aws_location = getattr(settings, "AWS_LOCATION", "")
    can_delete_aws_storage_files = getattr(
        settings, "CAN_DELETE_AWS_STORAGE_FILES", False)
    if not can_delete_aws_storage_files:
        print("No se pueden borrar archivos en AWS")
        return []
    if not s3_bucket:
        import boto3
        bucket_name = getattr(settings, "AWS_STORAGE_BUCKET_NAME")
        aws_access_key_id = getattr(settings, "AWS_ACCESS_KEY_ID")
        aws_secret_access_key = getattr(settings, "AWS_SECRET_ACCESS_KEY")
        s3 = boto3.resource(
            's3', aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key)
        s3_bucket = s3.Bucket(bucket_name)

    for i in range(0, len(files), delete_lote):
        delete_objects = [
            {'Key': aws_location + key}
            for key, _ in files[i:i+delete_lote]
        ]
        response = s3_bucket.delete_objects(
            Delete={'Objects': delete_objects})
        responses.append(response)
    return responses

